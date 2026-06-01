from pydantic import BaseModel


class NotificationTestResult(BaseModel):
    delivered: bool
    message: str
