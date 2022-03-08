# -*- coding: utf-8 -*-
from rest_framework import serializers

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"


class CollectionProjectSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)

    class Meta:
        model = Project
        exclude = ("relate_business",)


class CollectionTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True)
    create_time = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    creator_name = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    template_id = serializers.IntegerField(source="id", read_only=True)
    editor_name = serializers.CharField(read_only=True)
    edit_time = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    subprocess_has_update = serializers.BooleanField(read_only=True)
    has_subprocess = serializers.BooleanField(read_only=True)
    template_labels = serializers.SerializerMethodField(read_only=True)
    collection_id = serializers.SerializerMethodField(read_only=True)
    project = CollectionProjectSerializer(read_only=True)
    auth_actions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskTemplate
        exclude = ("collector",)

    def get_auth_actions(self, obj):
        return self.context["template_auth_actions"].get(obj.id, [])

    def get_template_labels(self, obj):
        return self.context["current_page_templates_labels"].get(obj.id, [])

    def get_collection_id(self, obj):
        return self.context["collection_id_template_id_map"][obj.id]
