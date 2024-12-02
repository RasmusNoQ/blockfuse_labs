import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"  # WebSocket URL

    # The event to send
    event = {
        "type": "event_1",
        "data": {"field1": "value1", "field2": "value2"},
        "timestamp": 1638316800.0,  # Example timestamp
    }

    try:
        # Connect to the WebSocket server
        async with websockets.connect(uri) as websocket:
            print("Connected to the WebSocket")

            # Send the event as a JSON message
            await websocket.send(json.dumps(event))
            print(f"Sent: {json.dumps(event)}")

            # Wait for the response from the server
            response = await websocket.recv()
            print(f"Received: {response}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(test_websocket())
