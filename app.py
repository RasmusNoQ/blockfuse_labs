import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Initialize FastAPI app
app = FastAPI()

# Home route
@app.get("/")
def home():
    return {"message": "Welcome to the Event WebSocket API!"}

# Database setup
DATABASE_URL = "sqlite:///./event_log.db"
db_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
db_session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
base = declarative_base()

# Define Event model
class EventRecord(base):
    __tablename__ = "event_records"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    event_data = Column(String)  # Store event data as JSON string
    event_timestamp = Column(Float)

base.metadata.create_all(bind=db_engine)

# WebSocket connection handler
class WebSocketManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


websocket_manager = WebSocketManager()

# Define valid event types and expected fields
VALID_EVENT_TYPES = {
    "event_1": ["field1", "field2"],
    "event_2": ["fieldA", "fieldB"],
    "event_3": ["paramX", "paramY", "paramZ"],
    "event_4": ["status", "description"],
    "event_5": ["username", "action"],
}

def validate_event_structure(event_type: str, event_data: dict):
    """Validate the structure of the event based on its type."""
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Invalid event type: {event_type}")
    expected_fields = VALID_EVENT_TYPES[event_type]
    missing_fields = [field for field in expected_fields if field not in event_data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    return True

# WebSocket endpoint to handle incoming events
@app.websocket("/ws")
async def event_websocket(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            incoming_message = await websocket.receive_text()
            try:
                # Parse and process the incoming event
                event = json.loads(incoming_message)
                event_type = event.get("type")
                event_data = event.get("data")
                event_timestamp = event.get("timestamp")

                if not event_type or not event_data or not event_timestamp:
                    raise ValueError("Invalid event format. Missing 'type', 'data', or 'timestamp'.")

                # Validate event structure
                validate_event_structure(event_type, event_data)

                # Store the event in the database
                db_session = db_session_local()
                new_event = EventRecord(
                    event_type=event_type, 
                    event_data=json.dumps(event_data), 
                    event_timestamp=event_timestamp
                )
                db_session.add(new_event)
                db_session.commit()
                db_session.refresh(new_event)
                db_session.close()

                # Send acknowledgment back to the WebSocket client
                await websocket.send_text(json.dumps({"status": "success", "event_id": new_event.id}))
            except Exception as e:
                await websocket.send_text(json.dumps({"status": "error", "error": str(e)}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# HTTP endpoint to retrieve events
@app.get("/events")
def fetch_events(event_type: str = None):
    """Fetch events from the database, optionally filtered by type."""
    db_session = db_session_local()
    query = db_session.query(EventRecord)
    if event_type:
        query = query.filter(EventRecord.event_type == event_type)
    events = query.all()
    db_session.close()
    return [{"id": event.id, "type": event.event_type, "data": json.loads(event.event_data), "timestamp": event.event_timestamp} for event in events]
