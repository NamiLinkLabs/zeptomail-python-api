from typing import Callable, Dict, Any, Optional, List, Union
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from zeptomail.webhooks.models import WebhookEvent, BounceEvent, OpenEvent, ClickEvent

webhook_router = APIRouter()

# Store registered handlers
_event_handlers: Dict[str, List[Callable]] = {
    "softbounce": [],
    "hardbounce": [],
    "email_open": [],
    "email_link_click": []
}

# Store authorized mailagent keys
_authorized_mailagent_keys: List[str] = []


def register_mailagent_key(mailagent_key: str) -> None:
    """Register an authorized mailagent key."""
    if mailagent_key not in _authorized_mailagent_keys:
        _authorized_mailagent_keys.append(mailagent_key)


def register_handler(event_type: str, handler: Callable) -> None:
    """Register a handler function for a specific event type."""
    if event_type not in _event_handlers:
        raise ValueError(f"Unknown event type: {event_type}")
    _event_handlers[event_type].append(handler)


async def validate_mailagent_key(request: Request) -> bool:
    """Validate that the webhook is from an authorized mailagent."""
    try:
        # Get the request body
        body = await request.body()
        body_text = body.decode('utf-8')
        
        # Parse the event data to get the mailagent_key
        event_data = WebhookEvent.model_validate_json(body_text)
        mailagent_key = event_data.mailagent_key
        
        # Check if this mailagent_key is authorized
        return mailagent_key in _authorized_mailagent_keys
    except Exception:
        return False


@webhook_router.post("/webhook")
async def handle_webhook(
    request: Request,
    authorized: bool = Depends(validate_mailagent_key)
) -> Dict[str, Any]:
    """Handle incoming ZeptoMail webhooks."""
    if not authorized:
        raise HTTPException(status_code=401, detail="Unauthorized mailagent_key")
    
    # Parse the webhook event
    body = await request.body()
    body_text = body.decode('utf-8')
    
    try:
        event = WebhookEvent.model_validate_json(body_text)
        
        # Process the event based on its type
        for event_type in event.event_name:
            if event_type in _event_handlers:
                # Create the appropriate event object based on the event type
                specialized_event: Union[BounceEvent, OpenEvent, ClickEvent, WebhookEvent]
                
                if event_type in ["softbounce", "hardbounce"]:
                    specialized_event = BounceEvent.model_validate_json(body_text)
                elif event_type == "email_open":
                    specialized_event = OpenEvent.model_validate_json(body_text)
                elif event_type == "email_link_click":
                    specialized_event = ClickEvent.model_validate_json(body_text)
                else:
                    specialized_event = event
                
                # Call all registered handlers for this event type
                for handler in _event_handlers[event_type]:
                    handler(specialized_event)
        
        return {"status": "success", "event_type": event.event_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {str(e)}")
