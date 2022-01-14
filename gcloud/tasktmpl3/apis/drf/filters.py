# -*- coding: utf-8 -*-
from django.db.models import Q
from django_filters import FilterSet, filters
from pipeline.models import PipelineTemplate
from gcloud.label.models import TemplateLabelRelation
from gcloud.tasktmpl3.models import TaskTemplate


class TaskTemplateFilter(FilterSet):
    label_ids = filters.CharFilter(method="filter_by_label_ids")
    subprocess_has_update = filters.BooleanFilter(method="filter_subprocess_has_update")
    has_subprocess = filters.BooleanFilter(field_name="pipeline_template__has_subprocess")

    def filter_by_label_ids(self, query, name, value):
        label_ids = [int(label_id) for label_id in value.strip().split(",")]
        template_ids = list(TemplateLabelRelation.objects.fetch_template_ids_using_union_labels(label_ids))
        condition = Q(id__in=template_ids)
        return query.filter(condition)

    def filter_subprocess_has_update(self, query, name, value):
        pipeline_template_ids = set(query.values_list("pipeline_template_id", flat=True))
        pipeline_template = PipelineTemplate.objects.filter(template_id__in=pipeline_template_ids)
        condition = [item.template_id for item in pipeline_template if item.subprocess_has_update == value]
        return query.filter(pipeline_template_id__in=condition)

    class Meta:
        model = TaskTemplate  # 模型名
        fields = {
            "pipeline_template__name": ["icontains"],
            "pipeline_template__edit_time": ["gte", "lte"],
            "pipeline_template__creator": ["contains"],
            "project_id": ["exact"],
        }
