from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import datetime

app = FastAPI(
    title="MedCenter Booking API",
    description="Mock external API for lab appointment scheduling.",
)


class BookingRequest(BaseModel):
    center_name: str
    time: str  # Expected format: YYYY-MM-DD HH:MM


class BookingResponse(BaseModel):
    message: str
    status: str


VALID_CENTERS = [
    "Downtown Medical Plaza",
    "Westside Imaging Lab",
    "Metro Central Annex",
]


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/book", response_model=BookingResponse)
def book_appointment(request: BookingRequest):
    if request.center_name not in VALID_CENTERS:
        raise HTTPException(
            status_code=400, detail=f"Invalid center. Must be one of {VALID_CENTERS}"
        )

    try:
        booking_time = datetime.datetime.strptime(request.time, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid time format. Please use 'YYYY-MM-DD HH:MM'.",
        )

    # Simulate a center being full at a specific time (e.g., 9 AM)
    if booking_time.hour == 9:
        raise HTTPException(
            status_code=409,
            detail="The center is fully booked at this time. Please choose another time.",
        )

    # Simulate business hours (e.g., 8 AM to 5 PM)
    if booking_time.hour < 8 or booking_time.hour >= 17:
        raise HTTPException(
            status_code=400,
            detail="Booking time is outside of business hours (8 AM - 5 PM).",
        )

    # Success response matches the verbatim requirement in AGENTS.md for the tool output
    message = f"Booking confirmed at {request.center_name} at {request.time}"
    return BookingResponse(message=message, status="success")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
