from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


class EmailAddress(BaseModel):
    address: str
    name: Optional[str] = None


class EmailAddressWrapper(BaseModel):
    email_address: EmailAddress


class EmailInfo(BaseModel):
    email_reference: str
    client_reference: Optional[str] = None
    is_smtp_trigger: bool = False
    subject: str
    bounce_address: Optional[str] = None
    from_: EmailAddress = Field(..., alias="from")
    to: List[EmailAddressWrapper] = []
    cc: Optional[List[EmailAddressWrapper]] = None
    bcc: Optional[List[EmailAddressWrapper]] = None
    reply_to: Optional[List[EmailAddress]] = None
    tag: Optional[str] = None
    processed_time: str
    object: Literal["email"] = "email"


class BounceDetails(BaseModel):
    reason: str
    bounced_recipient: str
    time: str
    diagnostic_message: str


class BounceData(BaseModel):
    details: List[BounceDetails]
    object: Literal["softbounce", "hardbounce"]


class IPLocationInfo(BaseModel):
    zipcode: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[str] = None
    country_name: Optional[str] = None
    ip_address: Optional[str] = None
    time_zone: Optional[str] = None
    region: Optional[str] = None
    longitude: Optional[str] = None


class ClientInfo(BaseModel):
    name: str
    version: str


class DeviceInfo(BaseModel):
    name: str


class OpenClickDetails(BaseModel):
    email_client: ClientInfo
    modified_time: str
    ip_location_info: IPLocationInfo
    browser: ClientInfo
    operating_system: ClientInfo
    time: str
    device: DeviceInfo
    user_agent: Optional[str] = None
    clicked_link: Optional[str] = None  # Only for link clicks


class OpenData(BaseModel):
    details: List[OpenClickDetails]
    object: Literal["email_open"] = "email_open"


class ClickData(BaseModel):
    details: List[OpenClickDetails]
    object: Literal["email_link_click"] = "email_link_click"


class EventMessage(BaseModel):
    email_info: EmailInfo
    event_data: List[Any]  # Can be BounceData, OpenData, or ClickData
    request_id: str


class WebhookEvent(BaseModel):
    event_name: List[str]
    event_message: List[EventMessage]
    mailagent_key: str
    webhook_request_id: str


# Specialized event types for easier handling
class BounceEvent(WebhookEvent):
    event_name: List[Literal["softbounce", "hardbounce"]]


class OpenEvent(WebhookEvent):
    event_name: List[Literal["email_open"]]


class ClickEvent(WebhookEvent):
    event_name: List[Literal["email_link_click"]]
