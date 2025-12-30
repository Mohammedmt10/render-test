import asyncio
import json
import websockets
import random

USERS = 200
ROOM_ID = "room-1"
WS_URL = "wss://render-test-6bid.onrender.com"

# Limit connection burst (important for Render)
SEM = asyncio.Semaphore(25)

async def simulate_user(user_id):
    async with SEM:
        try:
            async with websockets.connect(
                WS_URL,
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                # JOIN
                await ws.send(json.dumps({
                    "type": "join",
                    "userId": f"user-{user_id}",
                    "roomId": ROOM_ID
                }))

                await ws.recv()
                print(f"user-{user_id} joined")

                # DRAW EVENT
                await asyncio.sleep(random.uniform(0.2, 1.5))
                await ws.send(json.dumps({
                    "type": "draw",
                    "payload": {
                        "shape": "rect",
                        "x": random.randint(0, 800),
                        "y": random.randint(0, 600),
                        "width": 40,
                        "height": 40
                    }
                }))

                # Stay connected
                await asyncio.sleep(2)

        except Exception as e:
            print(f"user-{user_id} error: {e}")

async def main():
    await asyncio.gather(*[
        simulate_user(i)
        for i in range(1, USERS + 1)
    ])

asyncio.run(main())
