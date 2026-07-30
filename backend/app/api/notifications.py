from fastapi import APIRouter
from app.models.domain import Notification

router = APIRouter()

@router.get("/")
async def list_notifications():
    notifications = await Notification.find_all().to_list()
    return {"status": "success", "notifications": notifications}

@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    notification = await Notification.get(notification_id)
    if notification:
        notification.read = True
        await notification.save()
    return {"status": "success"}

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    notification = await Notification.get(notification_id)
    if notification:
        await notification.delete()
    return {"status": "success"}
