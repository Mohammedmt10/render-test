import asyncio
import json
import os
import websockets

rooms = {}

async def handler(websocket):
    user_id = None
    room_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            # JOIN ROOM
            if data.get("type") == "join":
                user_id = data.get("userId")
                room_id = data.get("roomId")

                if room_id not in rooms:
                    rooms[room_id] = set()

                rooms[room_id].add(websocket)

                await websocket.send(json.dumps({
                    "type": "joined",
                    "roomId": room_id
                }))

            # BROADCAST EVENTS
            elif data.get("type") == "draw" and room_id:
                payload = json.dumps({
                    "type": "draw",
                    "userId": user_id,
                    "payload": data.get("payload")
                })

                for client in list(rooms.get(room_id, [])):
                    if client != websocket:
                        try:
                            await client.send(payload)
                        except:
                            pass

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        # CLEANUP
        if room_id and room_id in rooms:
            rooms[room_id].discard(websocket)
            if not rooms[room_id]:
                del rooms[room_id]

async def main():
    port = int(os.environ.get("PORT", 8765))
    print(f"WebSocket running on 0.0.0.0:{port}")

    async with websockets.serve(
        handler,
        "0.0.0.0",
        port
    ):
        await asyncio.Future()


asyncio.run(main())
