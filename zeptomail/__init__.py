from .client import ZeptoMail
from .webhooks import webhook_router, WebhookEvent, BounceEvent, OpenEvent, ClickEvent

__version__ = "0.1.1"
__all__ = [
    "ZeptoMail",
    "webhook_router",
    "WebhookEvent",
    "BounceEvent",
    "OpenEvent",
    "ClickEvent"
]
