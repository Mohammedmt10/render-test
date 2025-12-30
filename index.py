import asyncio
import json
import os
import websockets

rooms = {}

def active_connections():
    return sum(len(v) for v in rooms.values())

async def handler(websocket):
    user_id = None
    room_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "join":
                user_id = data.get("userId")
                room_id = data.get("roomId")

                rooms.setdefault(room_id, set()).add(websocket)

                print(f"{user_id} joined {room_id}")
                print("Active connections:", active_connections())

                await websocket.send(json.dumps({
                    "type": "joined",
                    "roomId": room_id
                }))

            elif data.get("type") == "draw" and room_id:
                payload = json.dumps({
                    "type": "draw",
                    "userId": user_id,
                    "payload": data.get("payload")
                })

                for client in list(rooms.get(room_id, [])):
                    if client != websocket:
                        await client.send(payload)

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        if room_id and room_id in rooms:
            rooms[room_id].discard(websocket)
            if not rooms[room_id]:
                del rooms[room_id]

        print(f"{user_id} disconnected")
        print("Active connections:", active_connections())

async def main():
    port = int(os.environ.get("PORT", 10000))
    print(f"Listening on 0.0.0.0:{port}")

    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # KEEP PROCESS ALIVE

if __name__ == "__main__":
    asyncio.run(main())
