import uvicorn
from fastapi import FastAPI
from zeptomail import webhook_router, BounceEvent, OpenEvent, ClickEvent
from zeptomail.webhooks.router import register_mailagent_key, register_handler

app = FastAPI()

# Register the webhook router
app.include_router(webhook_router)

# Register your authorized mailagent key
register_mailagent_key("Zoho-enczapikey ....")  # Replace with your actual mailagent_key

# Define handlers for different event types
def handle_bounce(event: BounceEvent):
    """Handle bounce events."""
    print(f"Bounce event received: {event.event_name}")
    for message in event.event_message:
        for data in message.event_data:
            for detail in data.details:
                print(f"Bounce reason: {detail.reason}")
                print(f"Bounced recipient: {detail.bounced_recipient}")
                print(f"Diagnostic message: {detail.diagnostic_message}")

def handle_open(event: OpenEvent):
    """Handle email open events."""
    print(f"Email open event received")
    for message in event.event_message:
        for data in message.event_data:
            for detail in data.details:
                print(f"Opened at: {detail.time}")
                print(f"Device: {detail.device.name}")
                print(f"Browser: {detail.browser.name} {detail.browser.version}")

def handle_click(event: ClickEvent):
    """Handle link click events."""
    print(f"Link click event received")
    for message in event.event_message:
        for data in message.event_data:
            for detail in data.details:
                print(f"Clicked at: {detail.time}")
                print(f"Clicked link: {detail.clicked_link}")
                print(f"Device: {detail.device.name}")

# Register the handlers
register_handler("softbounce", handle_bounce)
register_handler("hardbounce", handle_bounce)
register_handler("email_open", handle_open)
register_handler("email_link_click", handle_click)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8500)
