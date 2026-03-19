#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看清理任务中的SQL语句
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection, reset_queries
from django.utils import timezone
from django.conf import settings
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.core.models import ProjectConfig
from django.db.models import Q

# 导入调试助手
from debug_sql_helper import print_queryset_sql, print_sql_queries, analyze_queryset


def check_filter_clean_task_instances_sql():
    """查看 filter_clean_task_instances 函数中的SQL"""

    print("\n" + "="*100)
    print("检查清理任务过滤逻辑的SQL")
    print("="*100 + "\n")

    validity_day = getattr(settings, 'V2_TASK_VALIDITY_DAY', 30)
    expire_time = timezone.now() - timezone.timedelta(days=validity_day)
    batch_num = getattr(settings, 'CLEAN_EXPIRED_V2_TASK_BATCH_NUM', 20)

    # 构建查询
    base_q = Q(
        pipeline_instance__create_time__lt=expire_time,
        engine_ver=2,
        pipeline_instance__is_expired=False,
    )

    # 简单查询（不考虑项目配置）
    qs = (
        TaskFlowInstance.objects.filter(base_q)
        .order_by("id")
        .values("id", "pipeline_instance__instance_id", "project_id", "create_method")[:batch_num]
    )

    print("\n1️⃣  基础过滤查询（带JOIN）")
    print_queryset_sql(qs, "filter_clean_task_instances")

    # 2. 检查实际数量
    count_qs = TaskFlowInstance.objects.filter(base_q)
    print("\n2️⃣  统计符合条件的任务数")
    analyze_queryset(count_qs, "待清理任务统计", execute=True)


def check_get_clean_pipeline_data_sql():
    """查看 get_clean_pipeline_instance_data 中的SQL"""

    print("\n" + "="*100)
    print("检查获取清理数据的SQL（以3个instance_id为例）")
    print("="*100 + "\n")

    from pipeline.models import PipelineInstance, TreeInfo, Snapshot
    from pipeline_web.core.models import NodeInInstance
    from pipeline.eri.models import (
        ContextValue, ContextOutputs, Process, State, Data,
        Node, ExecutionData, ExecutionHistory, Schedule, CallbackData
    )

    # 示例instance_ids
    test_instance_ids = ["test_id_1", "test_id_2", "test_id_3"]

    with print_sql_queries("获取清理数据"):
        # 1. PipelineInstance查询
        pipeline_instances = PipelineInstance.objects.filter(instance_id__in=test_instance_ids)
        print("\n1️⃣  查询 PipelineInstance")
        print_queryset_sql(pipeline_instances, "PipelineInstance")

        # 2. NodeInInstance查询
        nodes_in_pipeline = NodeInInstance.objects.filter(instance_id__in=test_instance_ids)
        print("\n2️⃣  查询 NodeInInstance")
        print_queryset_sql(nodes_in_pipeline, "NodeInInstance")

        # 3. ContextValue查询
        context_value = ContextValue.objects.filter(pipeline_id__in=test_instance_ids)
        print("\n3️⃣  查询 ContextValue")
        print_queryset_sql(context_value, "ContextValue")

        # 4. Process查询
        process = Process.objects.filter(root_pipeline_id__in=test_instance_ids)
        print("\n4️⃣  查询 Process")
        print_queryset_sql(process, "Process")

        print("\n注意: 实际执行时还会根据node_ids查询更多表（State, Data, Node等）")


def check_delete_queryset_sql():
    """查看删除操作的SQL"""

    print("\n" + "="*100)
    print("检查删除操作的SQL（不实际执行）")
    print("="*100 + "\n")

    from pipeline.eri.models import State

    # 示例：假设要删除某些State记录
    test_node_ids = ["node_1", "node_2", "node_3"]

    delete_qs = State.objects.filter(node_id__in=test_node_ids)

    print("\n删除State记录的SQL:")
    print_queryset_sql(delete_qs, "删除State")

    print("\n实际删除时会执行:")
    print("  1. SELECT 查询（获取要删除的记录）")
    print("  2. DELETE FROM ... WHERE id IN (...)")
    print("\n⚠️  Django的delete()会:")
    print("  - 先查询所有要删除的对象（触发信号）")
    print("  - 处理级联删除")
    print("  - 执行实际的DELETE语句")
    print("  这就是为什么大批量删除会占用大量内存和时间")


def check_update_queryset_sql():
    """查看更新操作的SQL"""

    print("\n" + "="*100)
    print("检查更新操作的SQL（不实际执行）")
    print("="*100 + "\n")

    from pipeline.models import PipelineInstance

    test_instance_ids = ["test_id_1", "test_id_2"]
    update_qs = PipelineInstance.objects.filter(instance_id__in=test_instance_ids)

    print("\n更新PipelineInstance的SQL:")
    print_queryset_sql(update_qs, "标记过期")

    print("\n实际执行 .update(is_expired=True) 时的SQL:")
    print("UPDATE `pipeline_pipelineinstance`")
    print("SET `is_expired` = 1")
    print("WHERE `instance_id` IN ('test_id_1', 'test_id_2')")
    print("\n✅ update()不会先查询对象，性能更好")


if __name__ == "__main__":
    import sys

    print("\n" + "🔍 Django QuerySet SQL 调试工具")
    print("="*100)

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n请选择要检查的SQL:")
        print("1. filter_clean_task_instances (过滤待清理任务)")
        print("2. get_clean_pipeline_data (获取清理数据)")
        print("3. delete操作 (删除SQL)")
        print("4. update操作 (更新SQL)")
        print("5. 全部检查")
        choice = input("\n输入选项 (1-5): ").strip()

    if choice == "1":
        check_filter_clean_task_instances_sql()
    elif choice == "2":
        check_get_clean_pipeline_data_sql()
    elif choice == "3":
        check_delete_queryset_sql()
    elif choice == "4":
        check_update_queryset_sql()
    elif choice == "5":
        check_filter_clean_task_instances_sql()
        check_get_clean_pipeline_data_sql()
        check_delete_queryset_sql()
        check_update_queryset_sql()
    else:
        print("❌ 无效选项")
        sys.exit(1)

    print("\n" + "="*100)
    print("✅ SQL检查完成")
    print("="*100 + "\n")






