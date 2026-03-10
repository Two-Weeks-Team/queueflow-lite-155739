from fastapi import APIRouter, HTTPException, Depends, Path, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime
from models import SessionLocal, Restaurant, Queue, Customer, Base, engine
from ai_service import call_inference

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class ContactInfo(BaseModel):
    phone: str = Field(..., min_length=5)

class JoinQueueRequest(BaseModel):
    name: str = Field(..., min_length=2)
    party_size: int = Field(..., gt=0)
    contact_info: ContactInfo

class JoinQueueResponse(BaseModel):
    queue_position: int
    estimated_wait_time: int

class PositionResponse(BaseModel):
    current_position: int
    estimated_wait_time: int

class PredictWaitRequest(BaseModel):
    restaurant_id: str
    party_size: int = Field(..., gt=0)

class PredictWaitResponse(BaseModel):
    predicted_wait_time: int

class SmartNotification(BaseModel):
    type: str
    message: str

class SmartNotificationsResponse(BaseModel):
    notifications: List[SmartNotification]

# ---------------------------------------------------------------------------
# Helper to fetch queue and ensure existence
# ---------------------------------------------------------------------------
def get_queue_or_404(queue_id: str, db) -> Queue:
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    return queue

# ---------------------------------------------------------------------------
# /api/queue/{queue_id}/join
# ---------------------------------------------------------------------------
@router.post("/api/queue/{queue_id}/join", response_model=JoinQueueResponse)
async def join_queue(
    queue_id: str = Path(..., description="Queue UUID"),
    payload: JoinQueueRequest = Body(...),
    db: SessionLocal = Depends(get_db),
):
    queue = get_queue_or_404(queue_id, db)

    # Determine next position
    next_position = queue.total_ahead + 1

    # Create Customer record
    cust = Customer(
        id=str(uuid.uuid4()),
        name=payload.name,
        phone=payload.contact_info.phone,
        email=None,
        queue_id=queue.id,
        position_in_queue=next_position,
        joined_at=datetime.utcnow(),
    )
    db.add(cust)

    # Update queue counters
    queue.total_ahead = next_position
    db.commit()
    db.refresh(cust)
    db.refresh(queue)

    # Predict wait time via AI
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that predicts restaurant wait times in minutes."},
            {"role": "user", "content": f"Predict wait time for a party of {payload.party_size} at restaurant {queue.restaurant_id}."}
        ]
        ai_result = await call_inference(messages)
        est_wait = int(ai_result.get("predicted_wait_time", 10))
    except Exception:
        est_wait = 10  # fallback static estimate

    # Store AI estimation (optional, demo purpose)
    # Not raising if table missing – ignore errors
    try:
        from models import AIEstimation
        est = AIEstimation(
            id=str(uuid.uuid4()),
            queue_id=queue.id,
            estimated_wait_time=est_wait,
            confidence=0.9,
        )
        db.add(est)
        db.commit()
    except Exception:
        pass

    return JoinQueueResponse(queue_position=next_position, estimated_wait_time=est_wait)

# ---------------------------------------------------------------------------
# /api/queue/{queue_id}/position
# ---------------------------------------------------------------------------
@router.get("/api/queue/{queue_id}/position", response_model=PositionResponse)
async def get_position(
    queue_id: str = Path(..., description="Queue UUID"),
    db: SessionLocal = Depends(get_db),
):
    queue = get_queue_or_404(queue_id, db)
    # For demo, we return the stored estimated_wait_time
    return PositionResponse(current_position=queue.current_position, estimated_wait_time=queue.estimated_wait_time)

# ---------------------------------------------------------------------------
# AI‑powered: Predict wait time (stand‑alone endpoint)
# ---------------------------------------------------------------------------
@router.post("/api/queue/predict-wait-time", response_model=PredictWaitResponse)
async def predict_wait_time_endpoint(req: PredictWaitRequest, db: SessionLocal = Depends(get_db)):
    messages = [
        {"role": "system", "content": "You are an AI model that returns a JSON object with a key 'predicted_wait_time' representing minutes as an integer."},
        {"role": "user", "content": f"Predict wait time for a party of {req.party_size} at restaurant {req.restaurant_id}."}
    ]
    result = await call_inference(messages)
    # result may already be a dict; ensure proper key
    predicted = result.get("predicted_wait_time")
    if predicted is None:
        predicted = 15  # fallback
    try:
        predicted_int = int(predicted)
    except Exception:
        predicted_int = 15
    return PredictWaitResponse(predicted_wait_time=predicted_int)

# ---------------------------------------------------------------------------
# AI‑powered: Smart notifications for a queue
# ---------------------------------------------------------------------------
@router.get("/api/queue/{queue_id}/smart-notifications", response_model=SmartNotificationsResponse)
async def smart_notifications(queue_id: str = Path(...), db: SessionLocal = Depends(get_db)):
    queue = get_queue_or_404(queue_id, db)
    messages = [
        {"role": "system", "content": "Generate a list of helpful notifications for a restaurant queue. Return JSON with an array of objects each having 'type' and 'message'."},
        {"role": "user", "content": f"Queue ID {queue_id} currently has {queue.total_ahead} parties waiting. Provide 2‑3 smart notifications."}
    ]
    result = await call_inference(messages)
    notifications_raw = result.get("notifications")
    notifications: List[Dict[str, Any]] = []
    if isinstance(notifications_raw, list):
        notifications = notifications_raw
    else:
        # fallback simple notification
        notifications = [{"type": "info", "message": "Your queue is moving smoothly."}]
    # Validate structure minimally
    validated = []
    for item in notifications:
        if isinstance(item, dict) and "type" in item and "message" in item:
            validated.append({"type": str(item["type"]), "message": str(item["message"])})
    if not validated:
        validated = [{"type": "info", "message": "No notifications available at this time."}]
    return SmartNotificationsResponse(notifications=validated)
