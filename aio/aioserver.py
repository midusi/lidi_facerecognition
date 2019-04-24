# server_simple.py
from aiohttp import web
import asyncio
import pickle


async def wshandle(request):
    variable = 1
    ws = web.WebSocketResponse()

    await ws.prepare(request)
    print(f"New connection {request}")
    while True:
        await asyncio.sleep(0.1)
        pickled=pickle.dumps(variable)
        await ws.send_bytes(pickled)
        variable+=1


app = web.Application()
app.add_routes([
                web.get("/echo", wshandle)])

web.run_app(app)