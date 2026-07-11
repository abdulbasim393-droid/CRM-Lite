from activity.models import (
    ActivityLog,
    ActionType,
    EntityType,
)


def log_activity(
    *,
    entity_type,
    entity_id,
    action,
    performed_by,
    old_value=None,
    new_value=None,
):
    """
    Creates an activity log entry.
    """

    ActivityLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        performed_by=performed_by,
    )