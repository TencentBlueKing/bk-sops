from rest_framework import serializers

from gcloud.iam_auth.conf import RESOURCE_TYPE_IDS


class ParentSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["project"])
    id = serializers.CharField(allow_blank=False)


class ListFilterSerializer(serializers.Serializer):
    parent = ParentSerializer(required=False)
    keyword = serializers.CharField(required=False, allow_blank=True, max_length=128)


class FetchFilterSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField(allow_blank=False), allow_empty=False, max_length=1000)


class PageSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1)
    page_size = serializers.IntegerField(min_value=1, max_value=1000)


class CallbackRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=RESOURCE_TYPE_IDS)
    method = serializers.ChoiceField(choices=["list_instance", "fetch_instance_info"])
    filter = serializers.DictField(required=False)
    page = PageSerializer(required=False)
    requires = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False)

    def validate(self, attrs):
        method = attrs["method"]
        filter_data = attrs.get("filter", {})
        if method == "list_instance":
            if "page" not in attrs:
                raise serializers.ValidationError({"page": "this field is required"})
            child = ListFilterSerializer(data=filter_data)
        else:
            if "page" in attrs:
                raise serializers.ValidationError({"page": "not allowed for fetch_instance_info"})
            child = FetchFilterSerializer(data=filter_data)
        child.is_valid(raise_exception=True)
        attrs["filter"] = child.validated_data
        requires = attrs.get("requires", [])
        if len(requires) != len(set(requires)):
            raise serializers.ValidationError({"requires": "duplicate field"})
        return attrs
