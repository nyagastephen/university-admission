from flask_login import current_user
from app.extensions import db
from app.models.application_log import ApplicationLog


def log_application_action(application_id, action, description):
    log = ApplicationLog(
        application_id=application_id,
        action=action,
        description=description,
        performed_by=current_user.id if current_user.is_authenticated else None
    )

    db.session.add(log)