#!/usr/bin/env python3
"""
Comprehensive UI flow test for the chat application with Faust integration
"""
import asyncio
import websockets
import json
import requests
import time

BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

def create_session():
    """Create a new chat session"""
    response = requests.post(f"{BASE_URL}/api/sessions")
    response.raise_for_status()
    return response.json()["session_id"]

def get_all_sessions():
    """Get all sessions"""
    response = requests.get(f"{BASE_URL}/api/sessions")
    response.raise_for_status()
    return response.json()

def get_session_messages(session_id):
    """Get messages for a session"""
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
    response.raise_for_status()
    return response.json()["messages"]

async def send_message_and_wait_response(session_id, message, timeout=30):
    """Send a message via WebSocket and wait for AI response"""
    uri = f"{WS_BASE_URL}/ws/{session_id}"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({"message": message}))
        print(f"  ✓ Sent: {message}")

        # Wait for ack
        ack = await asyncio.wait_for(websocket.recv(), timeout=5)
        ack_data = json.loads(ack)
        if ack_data.get("type") == "ack":
            print(f"  ✓ Acknowledged")

        # Wait for AI response
        response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        response_data = json.loads(response)

        if response_data.get("type") == "assistant":
            print(f"  ✓ AI Response: {response_data['message'][:100]}...")
            return response_data["message"]
        else:
            raise Exception(f"Unexpected response type: {response_data}")

async def main():
    print("=" * 80)
    print("COMPREHENSIVE UI FLOW TEST - FAUST INTEGRATION")
    print("=" * 80)
    print()

    # Test 1: Create a new session
    print("Test 1: Creating new session...")
    session_id = create_session()
    print(f"  ✓ Created session: {session_id}")
    print()

    # Test 2: Verify session in list
    print("Test 2: Verifying session appears in session list...")
    sessions = get_all_sessions()
    session_exists = any(s["session_id"] == session_id for s in sessions)
    if session_exists:
        print(f"  ✓ Session found in list")
    else:
        raise Exception("Session not found in list!")
    print()

    # Test 3: Send first message
    print("Test 3: Sending first message via WebSocket...")
    response1 = await send_message_and_wait_response(
        session_id,
        "Hello! Can you explain what Faust streaming library is in one sentence?"
    )
    print()

    # Test 4: Send second message
    print("Test 4: Sending second message via WebSocket...")
    response2 = await send_message_and_wait_response(
        session_id,
        "What are the main benefits of using Faust?"
    )
    print()

    # Test 5: Verify message history
    print("Test 5: Verifying message history...")
    messages = get_session_messages(session_id)
    expected_count = 4  # 2 user messages + 2 assistant responses
    if len(messages) == expected_count:
        print(f"  ✓ Found {expected_count} messages in history")
        for i, msg in enumerate(messages, 1):
            print(f"    {i}. [{msg['role']}]: {msg['content'][:60]}...")
    else:
        raise Exception(f"Expected {expected_count} messages but found {len(messages)}")
    print()

    # Test 6: Create second session and test concurrency
    print("Test 6: Testing multiple sessions...")
    session_id_2 = create_session()
    print(f"  ✓ Created second session: {session_id_2}")
    response3 = await send_message_and_wait_response(
        session_id_2,
        "Hi, what's a fun fact about streaming architectures?"
    )
    print()

    # Test 7: Verify both sessions maintain separate histories
    print("Test 7: Verifying session isolation...")
    messages_1 = get_session_messages(session_id)
    messages_2 = get_session_messages(session_id_2)

    if len(messages_1) == 4 and len(messages_2) == 2:
        print(f"  ✓ Session 1 has {len(messages_1)} messages")
        print(f"  ✓ Session 2 has {len(messages_2)} messages")
        print(f"  ✓ Sessions properly isolated")
    else:
        raise Exception(f"Session isolation failed! S1: {len(messages_1)}, S2: {len(messages_2)}")
    print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  • Faust stream processing: Working ✓")
    print("  • WebSocket communication: Working ✓")
    print("  • Session management: Working ✓")
    print("  • Message history: Working ✓")
    print("  • Multi-session support: Working ✓")
    print("  • End-to-end flow: Working ✓")
    print()

if __name__ == "__main__":
    asyncio.run(main())
