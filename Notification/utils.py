# notifications/utils.py

from .models import NotificationPreference, NotificationStep


def send_push_notification(user, title, body, extra=None):
    """
    TODO: call your existing webpush function here.
    """
    # Example:
    # from .push import send_web_push_to_user
    # send_web_push_to_user(user, title, body, extra=extra)
    pass


def send_in_app_message(user, title, body, extra=None):
    """
    If you have a Message model or use Django messages framework,
    do something here. For now, it's just a placeholder.
    """
    # Example with custom model:
    # Message.objects.create(user=user, title=title, body=body, data=extra)
    pass



# notifications/utils.py

from .models import NotificationStep, NotificationPreference

def notify_users_for_step(step_code, title, body):
    try:
        step = NotificationStep.objects.get(code=step_code)
    except NotificationStep.DoesNotExist:
        return

    prefs = NotificationPreference.objects.filter(step=step, enabled=True)

    for pref in prefs:
        if pref.channel in ["push", "both"]:
            send_push_notification(pref.user, title, body)
        
        if pref.channel in ["message", "both"]:
            send_in_app_message(pref.user, title, body)
