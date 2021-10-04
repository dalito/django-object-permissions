from django.conf import settings


def get_permission_for_model(model, action):
    """
    Resolve the named permission for a given model (or instance) and action (e.g. view or add).

    :param model: A model or instance
    :param action: View, add, change, or delete (string)
    """
    if action not in ('view', 'add', 'change', 'delete'):
        raise ValueError(f"Unsupported action: {action}")

    return '{}.{}_{}'.format(
        model._meta.app_label,
        action,
        model._meta.model_name
    )


def resolve_permission(name):
    """
    Given a permission name, return the app_label, action, and model_name components. For example, "dcim.view_site"
    returns ("dcim", "view", "site").

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    try:
        app_label, codename = name.split('.')
        action, model_name = codename.rsplit('_', 1)
    except ValueError:
        raise ValueError(
            f"Invalid permission name: {name}. Must be in the format <app_label>.<action>_<model>"
        )

    return app_label, action, model_name


def permission_is_exempt(name):
    """
    Determine whether a specified permission is exempt from evaluation.

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    app_label, action, model_name = resolve_permission(name)

    if action == 'view':
        if (
            # All models (excluding those in EXEMPT_EXCLUDE_MODELS) are exempt from view permission enforcement
            '*' in settings.EXEMPT_VIEW_PERMISSIONS and (app_label, model_name) not in settings.EXEMPT_EXCLUDE_MODELS
        ) or (
            # This specific model is exempt from view permission enforcement
            f'{app_label}.{model_name}' in settings.EXEMPT_VIEW_PERMISSIONS
        ):
            return True

    return False
