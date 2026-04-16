from fastapi import FastAPI
from pydantic import BaseModel
from Backend.Main import generate_event_plan

app = FastAPI()


class EventRequest(BaseModel):
    event_type: str
    event_date: str
    locality: str
    guest_count: int
    min_budget: int
    max_budget: int
    services: list[str]
    month: int


@app.post("/plan-event")
def plan_event(input_data: EventRequest):
    try:
        return generate_event_plan(input_data)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }