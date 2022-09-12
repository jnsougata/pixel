import aiohttp
import asyncio
import discord
from neocord import Bot
from extras.emoji import Emo


ROOT_API_URL = 'https://aiotube.deta.dev'


def form_id(url: str):
    if '/channel/' in url:
        return url.split('/')[-1]
    elif '/c/' in url:
        return url.split('/')[-1]
    elif '/user/' in url:
        return url.split('/')[-1]
    else:
        return url


async def fetch_channel_info(channel_id: str, session: aiohttp.ClientSession):
    resp = await session.get(f'{ROOT_API_URL}/channel/{channel_id}/info')
    if resp.status != 200:
        return channel_id, None
    return channel_id, await resp.json()


async def fetch_latest_uploaded(channel_id: str, session: aiohttp.ClientSession):
    resp = await session.get(f'{ROOT_API_URL}/channel/{channel_id}/latest_uploaded')
    if resp.status != 200:
        return channel_id, None
    return channel_id, await resp.json()


async def fetch_current_livestream(channel_id: str, session: aiohttp.ClientSession):
    resp = await session.get(f'{ROOT_API_URL}/channel/{channel_id}/livestream')
    if resp.status != 200:
        return channel_id, None
    return channel_id, await resp.json()


async def create_menu(bot: Bot, channel_ids: list):
    tasks = [fetch_channel_info(id, bot.session) for id in channel_ids]
    infos = await asyncio.gather(*tasks)
    options = [
        discord.SelectOption(label=info["name"], value=id, emoji=Emo.YT)
        for id, info in infos if info
    ]
    return options[:24]
