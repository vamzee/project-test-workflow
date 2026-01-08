#!/usr/bin/env python3
"""
Test streaming responses from the chat server
"""
import asyncio
import websockets
import json
import requests
import sys

BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

def create_session():
    """Create a new chat session"""
    response = requests.post(f"{BASE_URL}/api/sessions")
    response.raise_for_status()
    return response.json()["session_id"]

async def test_streaming(session_id, message):
    """Test streaming response via WebSocket"""
    uri = f"{WS_BASE_URL}/ws/{session_id}"

    print(f"Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("Connected!")

        # Send message
        await websocket.send(json.dumps({"message": message}))
        print(f"Sent: {message}\n")

        # Wait for acknowledgment
        ack = await websocket.recv()
        ack_data = json.loads(ack)
        if ack_data.get("type") == "ack":
            print("✓ Message acknowledged\n")

        # Receive streaming chunks
        print("Streaming response:")
        print("-" * 60)

        full_response = ""
        chunk_count = 0

        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60)
                data = json.loads(response)

                if data.get("type") == "assistant_chunk":
                    chunk = data.get("chunk", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                    chunk_count += 1

                elif data.get("type") == "assistant_done":
                    print("\n" + "-" * 60)
                    print(f"\n✓ Streaming complete!")
                    print(f"  Received {chunk_count} chunks")
                    print(f"  Total length: {len(full_response)} characters")
                    break

                elif data.get("type") == "assistant":
                    # Fallback for non-streaming
                    print(data.get("message"))
                    print("\n" + "-" * 60)
                    print("\n⚠ Received non-streaming response")
                    break

            except asyncio.TimeoutError:
                print("\n❌ Timeout waiting for response")
                break

        return full_response

async def main():
    print("=" * 60)
    print("STREAMING RESPONSE TEST")
    print("=" * 60)
    print()

    # Create session
    print("Creating new session...")
    session_id = create_session()
    print(f"✓ Session created: {session_id}\n")

    # Test streaming
    message = "Tell me an interesting fact about artificial intelligence and explain it in detail."
    await test_streaming(session_id, message)

if __name__ == "__main__":
    asyncio.run(main())
