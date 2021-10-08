import asyncio
from asynctube import Channel


async def main():
    channel = await Channel.fetch('UCU9FEimjiOV3zN_5kujbCMQ')
    latest = await channel.latest
    return latest.info



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    d = loop.run_until_complete(main())
    print(d['title'])