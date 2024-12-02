Event WebSocket API
A FastAPI-based WebSocket API that handles event data. Events are validated, stored in an SQLite database, and can be retrieved via an HTTP GET endpoint.

Features
WebSocket Support: Send events to the server via WebSocket.
Event Validation: Ensures events meet required field structure.
Database: SQLite for persistent event storage.
HTTP API: Retrieve events via GET requests.
Requirements
Python 3.7+
SQLite (automatically managed)
Dependencies: fastapi, uvicorn, sqlalchemy, pydantic
Setup
Clone the repository:


git clone https://github.com/your-username/event-websocket-api.git
cd event-websocket-api
Set up a virtual environment:

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt
Run the server:


uvicorn main:app --reload
The app will run at http://localhost:8000.

WebSocket Usage
Endpoint: ws://localhost:8000/ws

Message Format (JSON):

json

{
  "type": "event_1",        // Event type (e.g., "event_1")
  "data": {                 // Event data (e.g., { "field1": "value1", "field2": "value2" })
    "field1": "value1",
    "field2": "value2"
  },
  "timestamp": 1638316800.0 // Event timestamp (Unix epoch)
}
WebSocket Client Example (Python):


import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    event = {
        "type": "event_1",
        "data": {"field1": "value1", "field2": "value2"},
        "timestamp": 1638316800.0,
    }
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(event))
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())
HTTP API Usage
Retrieve Events:

Endpoint: GET /events
Optionally filter by event_type: GET /events?event_type=event_1
Response Example:

json

[
  {
    "id": 1,
    "type": "event_1",
    "data": {"field1": "value1", "field2": "value2"},
    "timestamp": 1638316800.0
  }
]
Database
SQLite database (event_log.db) stores events in the events table:

id: Integer (Primary Key)
type: String (Event type)
data: String (Event data, stored as JSON)
timestamp: Float (Event timestamp)
Event Types
The following event types are supported:

event_1: Requires field1, field2
event_2: Requires fieldA, fieldB
event_3: Requires paramX, paramY, paramZ
event_4: Requires status, description
event_5: Requires username, action
Error Handling
If an event is invalid or fields are missing, the server responds with:

json

{
  "status": "error",
  "error": "Missing required fields: ['field1']"
}
License
GNU 