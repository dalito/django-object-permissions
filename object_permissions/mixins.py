from django.contrib.auth.mixins import AccessMixin

from .utils import resolve_permission


class ObjectPermissionRequiredMixin(AccessMixin):
    """
    Similar to Django's built-in PermissionRequiredMixin, but extended to check for both model-level and object-level
    permission assignments. If the user has only object-level permissions assigned, the view's queryset is filtered
    to return only those objects on which the user is permitted to perform the specified action.

    additional_permissions: An optional iterable of statically declared permissions to evaluate in addition to those
                            derived from the object type
    """
    additional_permissions = list()

    def get_required_permission(self):
        """
        Return the specific permission necessary to perform the requested action on an object.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_required_permission()")

    def has_permission(self):
        user = self.request.user
        permission_required = self.get_required_permission()

        # Check that the user has been granted the required permission(s).
        if user.has_perms((permission_required, *self.additional_permissions)):

            # Update the view's QuerySet to filter only the permitted objects
            action = resolve_permission(permission_required)[1]
            self.queryset = self.queryset.restrict(user, action)

            return True

        return False

    def dispatch(self, request, *args, **kwargs):

        if not hasattr(self, 'queryset'):
            raise RuntimeError(
                '{} has no queryset defined. ObjectPermissionRequiredMixin may only be used on views which define '
                'a base queryset'.format(self.__class__.__name__)
            )

        if not self.has_permission():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
