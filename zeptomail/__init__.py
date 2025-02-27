from .client import ZeptoMail
from .webhooks import webhook_router, WebhookEvent, BounceEvent, OpenEvent, ClickEvent
from .errors import  ZeptoMailError
__all__ = [
    "ZeptoMail",
    "webhook_router",
    "WebhookEvent",
    "BounceEvent",
    "OpenEvent",
    "ClickEvent"
]
