# -*- coding: utf-8 -*-
"""
导出全量流程 Mako 表达式清单，并按 bamboo-engine PR #269 安全策略打标。

使用方法:
    python manage.py export_mako_expression_inventory --output /tmp/mako_exprs.csv
    python manage.py export_mako_expression_inventory --output /tmp/mako_exprs.csv --hits-only
    python manage.py export_mako_expression_inventory --output /tmp/mako_exprs.csv --project-id 23
    python manage.py export_mako_expression_inventory --output /tmp/mako_exprs.csv --bk-biz-id 1001,1002
    python manage.py export_mako_expression_inventory --output /tmp/mako_exprs.csv \\
        --base-url https://apps.example.com/o/bk_sops --skip-subprocess-exec

默认输出「所有流程里的全部 ${...}」。生产全量约 150 万行，建议先用
--hits-only 或 --project-id 缩小范围。

内存：按批流式扫描，一次只解压一棵流程树。子流程最近执行默认只查
TemplateRelationship + 父流程最近启动时间，不解开历史任务 execution_data。
"""

import csv
import gc
import logging
import resource
import sys
from collections import defaultdict

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import close_old_connections, reset_queries
from django.db.models import Count, Max
from django.utils import timezone
from pipeline.models import Snapshot

from gcloud.analysis_statistics.mako_expression_inventory import (
    chunked,
    collect_target_ancestors,
    find_subprocess_refs,
    iter_template_expressions,
    load_extra_whitelist,
    load_import_modules,
    yes_no,
)
from gcloud.clocked_task.models import ClockedTask
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import CLOCKED_TASK_NOT_STARTED, COMMON, PROJECT
from gcloud.core.models import Business, Project
from gcloud.periodictask.models import PeriodicTask
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("root")

CSV_FIELDS = [
    "风险档位",
    "命中安全策略",
    "命中无条件策略",
    "命中白名单策略",
    "命中原因",
    "使用注入模块",
    "注入模块名",
    "有深层属性调用",
    "属性链",
    "属性链深度",
    "根标识符",
    "v2引擎能匹配",
    "业务ID",
    "业务名称",
    "项目ID",
    "项目名称",
    "流程来源",
    "流程模板ID",
    "pipeline_template_id",
    "流程名称",
    "流程分类",
    "流程链接",
    "创建者",
    "最近更新者",
    "最近更新时间",
    "最近执行时间",
    "最近执行距今天数",
    "最近执行方式",
    "最近执行任务ID",
    "最近执行任务名称",
    "最近执行任务链接",
    "直接执行次数",
    "是否有启用周期任务",
    "是否有未启动计划任务",
    "位置类型",
    "JSON路径",
    "节点ID",
    "节点名称",
    "节点类型",
    "插件code",
    "表达式",
]


class Command(BaseCommand):
    help = "导出全量流程 Mako 表达式清单，并按 PR #269 安全策略打标"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, required=True, help="输出 CSV 路径")
        parser.add_argument(
            "--source",
            type=str,
            default="all",
            choices=("all", "project", "common"),
            help="扫描范围：项目流程 / 公共流程 / 全部，默认 all",
        )
        parser.add_argument(
            "--project-id",
            type=str,
            default=None,
            help="项目/业务空间 ID，逗号分隔",
        )
        parser.add_argument(
            "--bk-biz-id",
            type=str,
            default=None,
            help="CMDB 业务 ID，逗号分隔",
        )
        parser.add_argument(
            "--base-url",
            type=str,
            default=None,
            help="流程链接基础 URL，默认 settings.APP_HOST / BK_SOPS_HOST",
        )
        parser.add_argument(
            "--hits-only",
            action="store_true",
            help="只输出命中无条件策略或白名单硬规则的表达式，不含 unknown_root",
        )
        parser.add_argument(
            "--include-deleted",
            action="store_true",
            help="包含已删除流程，默认不包含",
        )
        parser.add_argument(
            "--skip-subprocess-exec",
            action="store_true",
            help="不回查「仅作为子流程被拉起」的最近执行",
        )
        parser.add_argument(
            "--verify-subprocess-exec",
            action="store_true",
            help="用父任务 execution_data 核实子流程引用；更准但更吃内存，默认关闭",
        )
        parser.add_argument(
            "--max-templates",
            type=int,
            default=0,
            help="最多扫描多少个流程，0 表示不限制，便于试跑",
        )
        parser.add_argument(
            "--progress-every",
            type=int,
            default=50,
            help="每处理多少个流程打印一次进度",
        )
        parser.add_argument(
            "--query-chunk-size",
            type=int,
            default=100,
            help="模板元数据/执行记录批量查询大小，默认 100",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        source = options["source"]
        project_ids = self._parse_int_ids(options.get("project_id"), "--project-id")
        bk_biz_ids = self._parse_int_ids(options.get("bk_biz_id"), "--bk-biz-id")
        base_url = options.get("base_url") or self._get_default_base_url()
        hits_only = options["hits_only"]
        include_deleted = options["include_deleted"]
        include_subprocess_exec = not options["skip_subprocess_exec"]
        verify_subprocess_exec = options["verify_subprocess_exec"] and include_subprocess_exec
        max_templates = options["max_templates"]
        progress_every = max(options["progress_every"], 1)
        chunk_size = max(options["query_chunk_size"], 10)

        if bk_biz_ids:
            matched = list(Project.objects.filter(bk_biz_id__in=bk_biz_ids).values_list("id", flat=True))
            if project_ids:
                project_ids = [item for item in project_ids if item in set(matched)]
            else:
                project_ids = matched
            if not project_ids:
                raise CommandError("按 --bk-biz-id 没有匹配到任何项目")

        import_modules = load_import_modules()
        extra_whitelist = load_extra_whitelist()
        project_map = self._load_project_map(project_ids)
        biz_name_map = self._load_business_names(project_map)
        total = self._count_templates(source, project_ids, include_deleted, max_templates)

        self.stdout.write("注入模块: {}".format(", ".join(sorted(import_modules.values()))))
        self.stdout.write("extra whitelist: {}".format(", ".join(sorted(extra_whitelist))))
        self.stdout.write("输出: {}".format(output_file))
        self.stdout.write("待扫描流程数: {}".format(total))
        self.stdout.write(
            "子流程最近执行: {}".format(
                "关闭" if not include_subprocess_exec else ("核实execution_data" if verify_subprocess_exec else "关系表近似")
            )
        )
        if total == 0:
            raise CommandError("没有匹配到流程模板")

        written = 0
        scanned = 0
        skipped_tree = 0
        risk_counter = defaultdict(int)
        policy_templates = set()

        with open(output_file, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
            writer.writeheader()

            for metas in self._iter_template_meta_chunks(
                source=source,
                project_ids=project_ids,
                include_deleted=include_deleted,
                max_templates=max_templates,
                project_map=project_map,
                chunk_size=chunk_size,
            ):
                exec_map = self._load_execution_maps_for_chunk(
                    metas,
                    include_subprocess_exec=include_subprocess_exec,
                    verify_subprocess_exec=verify_subprocess_exec,
                    chunk_size=chunk_size,
                )
                periodic_map = self._load_periodic_flags(metas, chunk_size)
                clocked_map = self._load_clocked_flags(metas, chunk_size)

                for meta in metas:
                    scanned += 1
                    tree = self._load_snapshot_tree(meta.get("snapshot_id"))
                    if tree is None:
                        skipped_tree += 1
                    else:
                        exec_info = exec_map.get((meta["source"], meta["template_id"]), {})
                        try:
                            for analysis in iter_template_expressions(
                                tree, import_modules=import_modules, extra_whitelist=extra_whitelist
                            ):
                                if hits_only and not analysis["hits_policy"]:
                                    continue
                                writer.writerow(
                                    self._build_row(
                                        meta=meta,
                                        analysis=analysis,
                                        exec_info=exec_info,
                                        biz_name_map=biz_name_map,
                                        periodic_map=periodic_map,
                                        clocked_map=clocked_map,
                                        base_url=base_url,
                                    )
                                )
                                written += 1
                                risk_counter[analysis["risk_level"]] += 1
                                if analysis["hits_policy"]:
                                    policy_templates.add((meta["source"], meta["template_id"]))
                        finally:
                            tree.clear()
                            del tree

                    if scanned % progress_every == 0:
                        self.stdout.write(
                            "进度: 已扫流程 {}/{}，已写表达式 {}，树加载失败 {}，rss={:.1f}MB".format(
                                scanned, total, written, skipped_tree, self._rss_mb()
                            )
                        )
                        self._release_idle_memory()

                del exec_map
                del periodic_map
                del clocked_map
                del metas
                self._release_idle_memory()

        self.stdout.write(self.style.SUCCESS("完成"))
        self.stdout.write("扫描流程: {}".format(scanned))
        self.stdout.write("树加载失败: {}".format(skipped_tree))
        self.stdout.write("输出行数: {}".format(written))
        self.stdout.write("命中安全策略的流程数: {}".format(len(policy_templates)))
        for level in ("无条件阻断", "仅enforce阻断", "潜在unknown_root", "解析失败", "无"):
            self.stdout.write("  {}: {}".format(level, risk_counter.get(level, 0)))

    def _template_queryset(self, model, source, project_ids, include_deleted):
        qs = model.objects.all()
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        if source == PROJECT and project_ids:
            qs = qs.filter(project_id__in=project_ids)
        return qs.order_by("id")

    def _count_templates(self, source, project_ids, include_deleted, max_templates):
        total = 0
        if source in ("all", "project"):
            total += self._template_queryset(TaskTemplate, PROJECT, project_ids, include_deleted).count()
        if source in ("all", "common"):
            total += self._template_queryset(CommonTemplate, COMMON, project_ids, include_deleted).count()
        if max_templates:
            return min(total, max_templates)
        return total

    def _iter_template_meta_chunks(self, source, project_ids, include_deleted, max_templates, project_map, chunk_size):
        yielded = 0
        specs = []
        if source in ("all", "project"):
            specs.append((PROJECT, TaskTemplate))
        if source in ("all", "common"):
            specs.append((COMMON, CommonTemplate))

        for current_source, model in specs:
            qs = self._template_queryset(model, current_source, project_ids, include_deleted)
            values_qs = qs.values(
                "id",
                "category",
                "pipeline_template_id",
                "pipeline_template__template_id",
                "pipeline_template__name",
                "pipeline_template__creator",
                "pipeline_template__editor",
                "pipeline_template__create_time",
                "pipeline_template__edit_time",
                "pipeline_template__snapshot_id",
            )
            if current_source == PROJECT:
                values_qs = qs.values(
                    "id",
                    "category",
                    "project_id",
                    "pipeline_template_id",
                    "pipeline_template__template_id",
                    "pipeline_template__name",
                    "pipeline_template__creator",
                    "pipeline_template__editor",
                    "pipeline_template__create_time",
                    "pipeline_template__edit_time",
                    "pipeline_template__snapshot_id",
                )
            chunk = []
            for row in values_qs.iterator(chunk_size=chunk_size):
                meta = self._row_to_meta(current_source, row, project_map)
                if not meta:
                    continue
                chunk.append(meta)
                yielded += 1
                if max_templates and yielded >= max_templates:
                    if chunk:
                        yield chunk
                    return
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk

    def _row_to_meta(self, source, row, project_map):
        pipeline_id = row.get("pipeline_template__template_id") or row.get("pipeline_template_id")
        if not pipeline_id:
            return None
        project_id = row.get("project_id") or ""
        project = project_map.get(project_id) or {}
        bk_biz_id = project.get("bk_biz_id") or ""
        if bk_biz_id and bk_biz_id <= 0:
            bk_biz_id = ""
        return {
            "source": source,
            "template_id": str(row["id"]),
            "pipeline_template_id": pipeline_id,
            "template_name": row.get("pipeline_template__name") or "",
            "category": row.get("category") or "",
            "creator": row.get("pipeline_template__creator") or "",
            "editor": row.get("pipeline_template__editor") or "",
            "edit_time": row.get("pipeline_template__edit_time") or row.get("pipeline_template__create_time"),
            "project_id": project_id,
            "project_name": project.get("name") or "",
            "bk_biz_id": bk_biz_id,
            "snapshot_id": row.get("pipeline_template__snapshot_id"),
        }

    def _load_project_map(self, project_ids):
        qs = Project.objects.all()
        if project_ids:
            qs = qs.filter(id__in=project_ids)
        return {row["id"]: row for row in qs.values("id", "name", "bk_biz_id")}

    def _load_business_names(self, project_map):
        biz_ids = sorted(
            {
                item.get("bk_biz_id")
                for item in project_map.values()
                if item.get("bk_biz_id") and item.get("bk_biz_id") > 0
            }
        )
        if not biz_ids:
            return {}
        return dict(Business.objects.filter(cc_id__in=biz_ids).values_list("cc_id", "cc_name"))

    def _load_snapshot_tree(self, snapshot_id):
        if not snapshot_id:
            return None
        try:
            data = Snapshot.objects.filter(id=snapshot_id).values_list("data", flat=True).first()
        except Exception:
            logger.exception("load snapshot failed: snapshot_id=%s", snapshot_id)
            return None
        return data if isinstance(data, dict) else None

    def _load_execution_maps_for_chunk(self, metas, include_subprocess_exec, verify_subprocess_exec, chunk_size):
        result = {}
        by_source = defaultdict(list)
        for meta in metas:
            by_source[meta["source"]].append(meta)

        for source, items in by_source.items():
            template_ids = [meta["template_id"] for meta in items]
            direct_latest, direct_counts = self._collect_direct_latest(source, template_ids, chunk_size)
            pipeline_ids = [meta["pipeline_template_id"] for meta in items]
            subprocess_latest = {}
            if include_subprocess_exec:
                subprocess_latest = self._collect_subprocess_latest(
                    pipeline_ids, chunk_size, verify=verify_subprocess_exec
                )
            for meta in items:
                direct = direct_latest.get(meta["template_id"], {})
                subprocess = subprocess_latest.get(meta["pipeline_template_id"], {})
                latest, latest_type = self._choose_latest(direct, subprocess)
                result[(source, meta["template_id"])] = {
                    "latest": latest,
                    "latest_type": latest_type,
                    "direct_count": direct_counts.get(meta["template_id"], 0),
                }
        return result

    def _collect_direct_latest(self, source, template_ids, chunk_size):
        latest = {}
        counts = {}
        for id_chunk in chunked(template_ids, chunk_size):
            stats = (
                TaskFlowInstance.objects.filter(
                    is_deleted=False,
                    template_source=source,
                    template_id__in=id_chunk,
                    pipeline_instance__start_time__isnull=False,
                )
                .values("template_id")
                .annotate(last_start=Max("pipeline_instance__start_time"), total=Count("id"))
            )
            last_start_by_tid = {}
            for row in stats:
                tid = str(row["template_id"])
                counts[tid] = row["total"]
                last_start_by_tid[tid] = row["last_start"]
            if not last_start_by_tid:
                continue
            tasks = TaskFlowInstance.objects.filter(
                is_deleted=False,
                template_source=source,
                template_id__in=list(last_start_by_tid.keys()),
                pipeline_instance__start_time__in=list(last_start_by_tid.values()),
            ).values(
                "id",
                "template_id",
                "project_id",
                "pipeline_instance__name",
                "pipeline_instance__start_time",
            )
            for item in tasks.iterator(chunk_size=chunk_size):
                tid = str(item["template_id"])
                if tid in latest:
                    continue
                if item["pipeline_instance__start_time"] != last_start_by_tid.get(tid):
                    continue
                latest[tid] = {
                    "time": item["pipeline_instance__start_time"],
                    "task_id": item["id"],
                    "task_name": item["pipeline_instance__name"] or "",
                    "project_id": item["project_id"],
                }
        return latest, counts

    def _collect_subprocess_latest(self, pipeline_ids, chunk_size, verify=False):
        target_to_ancestors = collect_target_ancestors(pipeline_ids)
        ancestor_ids = set()
        for ancestors in target_to_ancestors.values():
            ancestor_ids.update(ancestors)
        if not ancestor_ids:
            return {}

        parent_key_to_pipeline_id, pipeline_to_parent_keys = self._map_parent_templates(ancestor_ids, chunk_size)
        parent_latest = self._collect_parent_latest(pipeline_to_parent_keys, chunk_size)
        if verify:
            parent_latest = self._verify_parent_latest(
                parent_latest, pipeline_to_parent_keys, target_to_ancestors, chunk_size
            )

        latest = {}
        for target, ancestors in target_to_ancestors.items():
            chosen = {}
            for ancestor in ancestors:
                candidate = parent_latest.get(ancestor) or {}
                if not candidate.get("time"):
                    continue
                if not chosen or self._aware(candidate["time"]) > self._aware(chosen.get("time")):
                    chosen = candidate
            if chosen:
                latest[target] = chosen
        return latest

    def _map_parent_templates(self, parent_pipeline_ids, chunk_size):
        parent_key_to_pipeline_id = {}
        pipeline_to_parent_keys = defaultdict(list)
        for id_chunk in chunked(parent_pipeline_ids, chunk_size):
            for row in TaskTemplate.objects.filter(pipeline_template_id__in=id_chunk, is_deleted=False).values(
                "id", "pipeline_template_id"
            ):
                key = (PROJECT, str(row["id"]))
                pipeline_id = str(row["pipeline_template_id"])
                parent_key_to_pipeline_id[key] = pipeline_id
                pipeline_to_parent_keys[pipeline_id].append(key)
            for row in CommonTemplate.objects.filter(pipeline_template_id__in=id_chunk, is_deleted=False).values(
                "id", "pipeline_template_id"
            ):
                key = (COMMON, str(row["id"]))
                pipeline_id = str(row["pipeline_template_id"])
                parent_key_to_pipeline_id[key] = pipeline_id
                pipeline_to_parent_keys[pipeline_id].append(key)
        return parent_key_to_pipeline_id, pipeline_to_parent_keys

    def _collect_parent_latest(self, pipeline_to_parent_keys, chunk_size):
        parent_latest = {}
        by_source = defaultdict(list)
        key_to_pipeline = {}
        for pipeline_id, keys in pipeline_to_parent_keys.items():
            for source, template_id in keys:
                by_source[source].append(template_id)
                key_to_pipeline[(source, template_id)] = pipeline_id

        for source, template_ids in by_source.items():
            latest_by_tid, _counts = self._collect_direct_latest(source, template_ids, chunk_size)
            for template_id, info in latest_by_tid.items():
                pipeline_id = key_to_pipeline.get((source, template_id))
                if not pipeline_id:
                    continue
                current = parent_latest.get(pipeline_id) or {}
                if not current or self._aware(info.get("time")) > self._aware(current.get("time")):
                    copied = dict(info)
                    copied["via"] = "subprocess"
                    parent_latest[pipeline_id] = copied
        return parent_latest

    def _verify_parent_latest(self, parent_latest, pipeline_to_parent_keys, target_to_ancestors, chunk_size):
        """只核实每个父流程最近一条任务，避免把历史 execution_data 全解压进内存。"""
        ancestor_to_targets = defaultdict(set)
        for target, ancestors in target_to_ancestors.items():
            for ancestor in ancestors:
                ancestor_to_targets[ancestor].add(target)

        verified = {}
        for ancestor, info in parent_latest.items():
            task_id = info.get("task_id")
            if not task_id:
                continue
            row = TaskFlowInstance.objects.filter(id=task_id).values("pipeline_instance__execution_snapshot_id").first()
            if not row:
                continue
            tree = self._load_snapshot_tree(row.get("pipeline_instance__execution_snapshot_id"))
            try:
                refs = find_subprocess_refs(tree, ancestor_to_targets.get(ancestor, set()))
            finally:
                if isinstance(tree, dict):
                    tree.clear()
                del tree
            if refs:
                verified[ancestor] = info
        return verified

    def _choose_latest(self, direct, subprocess):
        direct_time = direct.get("time")
        sub_time = subprocess.get("time")
        if direct_time and sub_time:
            if self._aware(sub_time) > self._aware(direct_time):
                return subprocess, "作为子流程执行"
            return direct, "直接执行"
        if sub_time:
            return subprocess, "作为子流程执行"
        if direct_time:
            return direct, "直接执行"
        return {}, ""

    def _load_periodic_flags(self, templates, chunk_size):
        flags = {}
        by_source = defaultdict(list)
        for meta in templates:
            by_source[meta["source"]].append(meta["template_id"])
        for source, ids in by_source.items():
            for id_chunk in chunked(ids, chunk_size):
                rows = (
                    PeriodicTask.objects.filter(
                        template_source=source,
                        template_id__in=id_chunk,
                        task__celery_task__enabled=True,
                    )
                    .values_list("template_id", flat=True)
                    .distinct()
                )
                for template_id in rows:
                    flags[(source, str(template_id))] = True
        return flags

    def _load_clocked_flags(self, templates, chunk_size):
        flags = {}
        by_source = defaultdict(list)
        for meta in templates:
            by_source[meta["source"]].append(int(meta["template_id"]))
        for source, ids in by_source.items():
            for id_chunk in chunked(ids, chunk_size):
                rows = (
                    ClockedTask.objects.filter(
                        template_source=source,
                        template_id__in=id_chunk,
                        state=CLOCKED_TASK_NOT_STARTED,
                    )
                    .values_list("template_id", flat=True)
                    .distinct()
                )
                for template_id in rows:
                    flags[(source, str(template_id))] = True
        return flags

    def _build_row(self, meta, analysis, exec_info, biz_name_map, periodic_map, clocked_map, base_url):
        latest = exec_info.get("latest") or {}
        latest_time = latest.get("time")
        biz_id = meta["bk_biz_id"]
        return {
            "风险档位": analysis["risk_level"],
            "命中安全策略": yes_no(analysis["hits_policy"]),
            "命中无条件策略": yes_no(analysis["hits_unconditional"]),
            "命中白名单策略": yes_no(analysis["hits_whitelist"]),
            "命中原因": "|".join(analysis["reasons"]),
            "使用注入模块": yes_no(analysis["uses_injected_module"]),
            "注入模块名": ",".join(analysis["used_modules"]),
            "有深层属性调用": yes_no(analysis["has_deep_attr"]),
            "属性链": ",".join(analysis["attr_chains"]),
            "属性链深度": analysis["attr_depth"],
            "根标识符": ",".join(analysis["root_names"]),
            "v2引擎能匹配": yes_no(analysis["v2_matchable"]),
            "业务ID": biz_id,
            "业务名称": biz_name_map.get(biz_id, ""),
            "项目ID": meta["project_id"],
            "项目名称": meta["project_name"],
            "流程来源": meta["source"],
            "流程模板ID": meta["template_id"],
            "pipeline_template_id": meta["pipeline_template_id"],
            "流程名称": meta["template_name"],
            "流程分类": meta["category"],
            "流程链接": self._build_template_url(base_url, meta),
            "创建者": meta["creator"],
            "最近更新者": meta["editor"],
            "最近更新时间": self._fmt_dt(meta["edit_time"]),
            "最近执行时间": self._fmt_dt(latest_time),
            "最近执行距今天数": self._age_days(latest_time),
            "最近执行方式": exec_info.get("latest_type") or "",
            "最近执行任务ID": latest.get("task_id") or "",
            "最近执行任务名称": latest.get("task_name") or "",
            "最近执行任务链接": self._build_task_url(base_url, latest),
            "直接执行次数": exec_info.get("direct_count") or 0,
            "是否有启用周期任务": yes_no(periodic_map.get((meta["source"], meta["template_id"]), False)),
            "是否有未启动计划任务": yes_no(clocked_map.get((meta["source"], meta["template_id"]), False)),
            "位置类型": analysis["location_type"],
            "JSON路径": analysis["path"],
            "节点ID": analysis["node_id"],
            "节点名称": analysis["node_name"],
            "节点类型": analysis["node_type"],
            "插件code": analysis["plugin_code"],
            "表达式": analysis["expr"],
        }

    def _build_template_url(self, base_url, meta):
        if not base_url:
            return ""
        base = base_url.rstrip("/")
        if meta["source"] == COMMON:
            return "{}/template/common/view/?template_id={}&common=1".format(base, meta["template_id"])
        if not meta["project_id"]:
            return ""
        return "{}/template/view/{}/?template_id={}".format(base, meta["project_id"], meta["template_id"])

    def _build_task_url(self, base_url, latest):
        if not base_url or not latest.get("task_id") or not latest.get("project_id"):
            return ""
        return "{}/taskflow/execute/{}/?instance_id={}".format(
            base_url.rstrip("/"), latest["project_id"], latest["task_id"]
        )

    def _get_default_base_url(self):
        return getattr(settings, "APP_HOST", None) or getattr(settings, "BK_SOPS_HOST", "") or ""

    def _aware(self, value):
        if not value:
            return value
        try:
            if timezone.is_naive(value):
                return timezone.make_aware(value, timezone.get_current_timezone())
            return timezone.localtime(value)
        except Exception:
            return value

    def _fmt_dt(self, value):
        value = self._aware(value)
        if not value:
            return ""
        try:
            return value.strftime("%Y-%m-%d %H:%M:%S %z")
        except Exception:
            return str(value)

    def _age_days(self, value):
        value = self._aware(value)
        if not value:
            return ""
        try:
            return str((timezone.localtime(timezone.now()) - value).days)
        except Exception:
            return ""

    def _release_idle_memory(self):
        close_old_connections()
        if settings.DEBUG:
            reset_queries()
        gc.collect()

    def _rss_mb(self):
        try:
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return rss / (1024.0 * 1024.0)
            return rss / 1024.0
        except Exception:
            return -1.0

    def _parse_int_ids(self, raw_value, option_name):
        if raw_value in (None, ""):
            return []
        ids = []
        seen = set()
        for value in str(raw_value).split(","):
            value = value.strip()
            if not value:
                continue
            try:
                number = int(value)
            except ValueError:
                raise CommandError("{} 包含非法整数: {}".format(option_name, value))
            if number in seen:
                continue
            seen.add(number)
            ids.append(number)
        return ids


__all__ = ["Command", "CSV_FIELDS"]
