import sys
import discord
import json
import asyncio
import traceback
from .builder import SlashCommand
from dataclasses import dataclass
from discord.http import Route
from functools import wraps
from discord.utils import _to_json
from .appctx import ApplicationContext
from .base import BaseInteraction, BaseInteractionData, BaseSlashOption, BaseAppCommand
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable
import importlib
from discord.ext.commands import Bot


class Client(Bot):
    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
    ):
        super().__init__(
            intents=intents,
            command_prefix=command_prefix,
            enable_debug_events=True,
            help_command=help_command,
        )
        self._check = False
        self._command_pool = {}
        self._reg_queue = []
        self.slash_commands = {}

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        self._reg_queue.append((guild_id, command.to_dict))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.to_dict["name"]] = wrapper()
        return decorator

    async def _register(self):
        await self.wait_until_ready()
        if not self._check:
            self._check = True
            for guild_id, payload in self._reg_queue:
                if guild_id:
                    route = Route('POST', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
                else:
                    route = Route('POST', f'/applications/{self.user.id}/commands')
                self.slash_commands[payload['name']] = await self.http.request(route, json=payload)

    async def _invoke(self, interaction: ApplicationContext):
        pool = self._command_pool
        func = pool.get(interaction.name)
        if func:
            try:
                await func(interaction)
            except Exception:
                traceback.print_exc()

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self._register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = BaseInteraction(**response.get('d'))
            if interaction.type == 2:
                await self._invoke(ApplicationContext(interaction, self))

    def add_slash(self, command: SlashCommand, function: Callable, guild_id:  Optional[int] = None):
        self._reg_queue.append((guild_id, command.to_dict))
        self._command_pool[command.name] = function

    async def fetch_application_commands(self, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('GET', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
        else:
            route = Route('GET', f'/applications/{self.user.id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def delete_application_command(self, command_id: int, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('DELETE', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.user.id}/commands/{command_id}')
        try:
            await self.http.request(route)
        except discord.errors.NotFound:
            raise ValueError(f'Command with id [{command_id}] and guild [{guild_id}] not found')
