# -*- coding: utf-8 -*-
import json
import logging

from gcloud.core.apis.drf.serilaziers import UpdateDraftPipelineTreeSerializer

logger = logging.getLogger("root")


class DraftTemplateViewSetMixin:
    def get_draft(self, manager, template, username):
        # 如果模板draft_template_id为空，说明该模板还没有生成草稿，此时需要先创建一个草稿
        if template.draft_template_id is None:
            manager.create_draft(template=template, editor=username)
        return {
            "editor": template.draft_template.editor,
            "pipeline_tree": json.dumps(template.draft_pipeline_tree),
            "edit_time": template.draft_template.edit_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def update_template_draft(self, manager, template, request):
        serializer = UpdateDraftPipelineTreeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data["labels"] = serializer.validated_data.pop("template_labels", [])
        result = manager.update_draft_pipeline(
            template.draft_template, request.user.username, serializer.validated_data
        )
        return result

    def publish_template_draft(self, manager, template, username):
        return manager.publish_draft_pipeline(template=template, editor=username)

    def discard_template_draft(self, manager, template, username):
        return manager.discard_draft(template, username)
