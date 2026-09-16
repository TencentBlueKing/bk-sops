class IAMV4Error(Exception):
    pass


class IAMV4ProtocolError(IAMV4Error):
    pass


class IAMV4Unavailable(IAMV4Error):
    def __init__(self, message="IAM V4 service unavailable", request_id=""):
        self.request_id = request_id
        super().__init__(message)


class IAMResourceNotFound(IAMV4Error):
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = str(resource_id)
        super().__init__("{} resource was not found".format(resource_type))


class IAMPermissionDenied(Exception):
    def __init__(self, missing_permissions):
        self.missing_permissions = tuple(missing_permissions)
        super().__init__("IAM permission denied")


class AuthFailedException(Exception):
    def __init__(self, system, subject, action, resources):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources = resources
        super().__init__("IAM permission denied")

    def perms_apply_data(self):
        from gcloud.iam_auth.presentation import serialize_missing_permissions
        from gcloud.iam_auth.types import PermissionCheck

        resource = self.resources[0] if self.resources else None
        return serialize_missing_permissions([PermissionCheck(self.action.id, resource)])


class MultiAuthFailedException(AuthFailedException):
    def perms_apply_data(self):
        from gcloud.iam_auth.presentation import serialize_missing_permissions
        from gcloud.iam_auth.types import PermissionCheck

        resources = []
        for item in self.resources:
            if isinstance(item, (list, tuple)):
                resources.extend(item)
            else:
                resources.append(item)
        return serialize_missing_permissions([PermissionCheck(self.action.id, item) for item in resources])


class RawAuthFailedException(Exception):
    def __init__(self, permissions):
        self.permissions = permissions
        super().__init__("IAM permission denied")

    def perms_apply_data(self):
        return self.permissions
