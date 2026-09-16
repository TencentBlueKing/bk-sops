from rest_framework import serializers

from gcloud.iam_auth.conf import RESOURCE_TYPE_IDS


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError({key: ["unknown field"] for key in sorted(unknown)})
        return super().to_internal_value(data)


class SubjectSerializer(StrictSerializer):
    type = serializers.ChoiceField(choices=["user"])
    id = serializers.CharField(allow_blank=False)


class AuthResourceSerializer(StrictSerializer):
    id = serializers.CharField(allow_blank=False)


class DirectAuthRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    subject = SubjectSerializer()
    action_id = serializers.CharField(allow_blank=False)
    resource = AuthResourceSerializer(required=False, allow_null=True)


class DirectAuthByActionsRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    subject = SubjectSerializer()
    action_ids = serializers.ListField(child=serializers.CharField(allow_blank=False), allow_empty=False)
    resource = AuthResourceSerializer(required=False, allow_null=True)


class DirectAuthByResourcesRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    subject = SubjectSerializer()
    action_id = serializers.CharField(allow_blank=False)
    resources = AuthResourceSerializer(many=True, allow_empty=False)


class ListAuthorizedResourceRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    subject = SubjectSerializer()
    action_id = serializers.CharField(allow_blank=False)


class ApplyAncestorSerializer(StrictSerializer):
    type = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS)
    id = serializers.CharField(allow_blank=False)


class ApplyResourceSerializer(StrictSerializer):
    type = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS)
    id = serializers.CharField(allow_blank=False)
    ancestors = ApplyAncestorSerializer(many=True, required=False)


class PermissionApplySerializer(StrictSerializer):
    action_id = serializers.CharField(allow_blank=False)
    resources = ApplyResourceSerializer(many=True, required=False)


class GenerateApplyURLRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    permissions = PermissionApplySerializer(many=True, allow_empty=False)


class RetrieveCallbackTokenRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)


class SystemSerializer(StrictSerializer):
    id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
    managers = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False)
    clients = serializers.ListField(child=serializers.CharField(allow_blank=False), allow_empty=False)
    callback_url = serializers.CharField(required=False, allow_blank=True)


class CreateSystemRequestSerializer(SystemSerializer):
    tenant_id = serializers.CharField(allow_blank=False)


class RetrieveSystemRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)


class UpdateSystemRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
    managers = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False)
    clients = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False, allow_empty=False)
    callback_url = serializers.CharField(required=False, allow_blank=True)


class ResourceTypeSerializer(StrictSerializer):
    id = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS)
    name = serializers.CharField(allow_blank=False)
    ancestors = serializers.ListField(child=serializers.ChoiceField(choices=RESOURCE_TYPE_IDS), required=False)


class BatchCreateResourceTypeRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    resource_types = ResourceTypeSerializer(many=True, allow_empty=False)


class ListModelObjectRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=100)


class UpdateResourceTypeRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    resource_type_id = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS)
    name = serializers.CharField(required=False, allow_blank=False)
    ancestors = serializers.ListField(child=serializers.ChoiceField(choices=RESOURCE_TYPE_IDS), required=False)


class ActionSerializer(StrictSerializer):
    id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(allow_blank=False)
    resource_type_id = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS, required=False, allow_blank=True)


class BatchCreateActionRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    actions = ActionSerializer(many=True, allow_empty=False)


class UpdateActionRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    action_id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(allow_blank=False)


class RoleActionSerializer(StrictSerializer):
    id = serializers.CharField(allow_blank=False)
    resource_type_id = serializers.CharField(required=False, allow_blank=True)


class RoleSerializer(StrictSerializer):
    id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
    actions = RoleActionSerializer(many=True, allow_empty=False)


class BatchCreateRoleRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    roles = RoleSerializer(many=True, allow_empty=False)


class UpdateRoleRequestSerializer(StrictSerializer):
    tenant_id = serializers.CharField(allow_blank=False)
    system_id = serializers.CharField(allow_blank=False)
    role_id = serializers.CharField(allow_blank=False)
    name = serializers.CharField(required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
