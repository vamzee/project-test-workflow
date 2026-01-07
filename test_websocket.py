#!/usr/bin/env python3
"""
Simple WebSocket test client for testing the chat system end-to-end
"""
import asyncio
import websockets
import json
import sys

async def test_chat(session_id, message):
    uri = f"ws://localhost:8000/ws/{session_id}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Sending message...")

            # Send message
            await websocket.send(json.dumps({"message": message}))
            print(f"Sent: {message}")

            # Wait for acknowledgment
            ack_response = await websocket.recv()
            ack = json.loads(ack_response)
            print(f"Received ack: {ack}")

            # Wait for AI response
            print("Waiting for AI response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            response_data = json.loads(response)
            print(f"\nAI Response: {response_data['message']}\n")
            print("✅ Test successful!")

    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    session_id = sys.argv[1] if len(sys.argv) > 1 else "6941346f-7f0e-4b73-932b-8e28a855b9ba"
    message = sys.argv[2] if len(sys.argv) > 2 else "Hello! Can you tell me a fun fact about Python programming?"

    asyncio.run(test_chat(session_id, message))
