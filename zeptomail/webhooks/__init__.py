try:
    from .router import webhook_router, register_mailagent_key, register_handler
    from .models import WebhookEvent, BounceEvent, OpenEvent, ClickEvent

    __all__ = [
        "webhook_router",
        "register_mailagent_key", 
        "register_handler",
        "WebhookEvent",
        "BounceEvent",
        "OpenEvent",
        "ClickEvent"
    ]
except ImportError as e:
    raise ImportError(
        "Webhook functionality requires FastAPI dependencies. "
        "Install with: pip install zeptomail-python-api[webhooks]"
    ) from e
