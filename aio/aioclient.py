#!/usr/bin/env python3
"""websocket cmd client for wssrv.py example."""
import argparse
import asyncio
import signal
import sys

import aiohttp

import pickle

async def start_client(loop, url):



    async def dispatch():
        while True:
            msg = await ws.receive()

            if msg.type == aiohttp.WSMsgType.BINARY:
                variable=pickle.loads(msg.data)
                print('Binary: ', msg.data)
                print(f"Variable: {variable}")
            else:
                if msg.type == aiohttp.WSMsgType.CLOSE:
                    await ws.close()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('Error during receive %s' % ws.exception())
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    pass

                break

    # send request
    async with aiohttp.ClientSession() as session:
        print(f"session: {session}")
        async with session.ws_connect(url) as ws:
           print(f"ws {ws}")
           await dispatch()


ARGS = argparse.ArgumentParser(
    description="websocket console client for wssrv.py example.")
ARGS.add_argument(
    '--host', action="store", dest='host',
    default='127.0.0.1', help='Host name')
ARGS.add_argument(
    '--port', action="store", dest='port',
    default=8080, type=int, help='Port number')

if __name__ == '__main__':
    args = ARGS.parse_args()
    if ':' in args.host:
        args.host, port = args.host.split(':', 1)
        args.port = int(port)

    url = 'http://{}:{}/echo'.format(args.host, args.port)
    print(f"Connecting to {url}")
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.create_task(start_client(loop, url))

loop.run_forever()