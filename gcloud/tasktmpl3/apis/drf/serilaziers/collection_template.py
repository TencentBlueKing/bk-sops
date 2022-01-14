# -*- coding: utf-8 -*-
import pytz
import settings

from rest_framework import serializers

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"


class ProjectSerializer(serializers.ModelSerializer):
    create_at = serializers.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ('relate_business',)

    def get_create_at(self, obj):
        return timezone_set(obj.create_at)


class CollectionTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(read_only=True)
    create_time = serializers.SerializerMethodField(read_only=True)
    creator_name = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    template_id = serializers.SerializerMethodField(read_only=True)
    editor_name = serializers.SerializerMethodField(read_only=True)
    edit_time = serializers.SerializerMethodField(read_only=True)
    subprocess_has_update = serializers.SerializerMethodField(read_only=True)
    has_subprocess = serializers.SerializerMethodField(read_only=True)
    template_labels = serializers.SerializerMethodField(read_only=True)
    collection_id = serializers.SerializerMethodField(read_only=True)
    project = ProjectSerializer(read_only=True)
    auth_actions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskTemplate
        exclude = ('collector',)

    def get_name(self, obj):
        return obj.name

    def get_auth_actions(self, obj):
        return self.context["template_auth_actions"].get(obj.id, [])

    def get_template_labels(self, obj):
        return self.context["current_page_templates_labels"].get(obj.id, [])

    def get_has_subprocess(self, obj):
        return obj.has_subprocess

    def get_subprocess_has_update(self, obj):
        return obj.subprocess_has_update

    def get_template_id(self, obj):
        return obj.template_id

    def get_create_time(self, obj):
        return timezone_set(obj.create_time)

    def get_edit_time(self, obj):
        return timezone_set(obj.edit_time)

    def get_category_name(self, obj):
        return obj.category_name

    def get_creator_name(self, obj):
        return obj.creator_name

    def get_editor_name(self, obj):
        return obj.editor_name

    def get_collection_id(self, obj):
        return self.context["collection_id_template_id_map"][obj.id]


def timezone_set(value):
    tz = pytz.timezone(settings.TIME_ZONE)
    return value.astimezone(tz=tz).strftime(DATETIME_FORMAT)
