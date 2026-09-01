import asyncio
import json
import websockets

async def test_websocket():
    url = "ws://localhost:8000/ws/chat/abimanyu123"
    print(f"Connecting to WebSocket: {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("Connected! Sending message...")
            
            payload = {
                "message": "siapa sih prof WHO?"
            }
            await websocket.send(json.dumps(payload))
            
            print("\n--- GEMINI STREAMING RESPONSE ---")
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "stream":
                    print(data.get("content"), end="", flush=True)
                elif data.get("type") == "done":
                    print("\n\n--- STREAMING COMPLETED ---")
                    break
                elif data.get("type") == "error":
                    print(f"\nError: {data.get('content')}")
                    break
    except Exception as e:
        print(f"Failed to connect or communicate: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
