import json
import discord
from discord.webhook.async_ import Webhook
from .base import BaseInteraction, BaseInteractionData, BaseSlashOption
from discord.http import Route
from discord.utils import _to_json
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable


class ApplicationContext:
    def __init__(self, interaction: BaseInteraction, client: discord.Client):
        self._interaction = interaction
        self._client = client

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._interaction.data.get('name')

    @property
    def id(self):
        return self._interaction.id

    @property
    def version(self):
        return self._interaction.version

    @property
    def data(self):
        return BaseInteractionData(**self._interaction.data)

    @property
    def options(self):
        return [BaseSlashOption(**option) for option in self.data.options]

    @property
    def application_id(self):
        return self._interaction.application_id

    @property
    def locale(self):
        return self._interaction.locale

    @property
    def guild_locale(self):
        return self._interaction.guild_locale

    @property
    def channel(self):
        channel_id = self._interaction.channel_id
        if channel_id:
            return self._client.get_channel(int(channel_id))

    @property
    def guild(self):
        guild_id = self._interaction.guild_id
        if guild_id:
            return self._client.get_guild(int(guild_id))

    @property
    def author(self):
        if self._interaction.guild_id:
            user_id = self._interaction.member.get('user').get('id')
            return self.guild.get_member(int(user_id))
        else:
            user_id = self._interaction.user.get('id')
            return self._client.get_user(int(user_id))

    @property
    def send(self):
        return self.channel.send

    async def respond(
            self,
            content: Union[str, Any] = None,
            *,
            tts: bool = False,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[Iterable[Optional[discord.Embed]]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            view: Optional[discord.ui.View] = None,
            views: Optional[Iterable[discord.ui.View]] = None,
            ephemeral: bool = False
    ):
        form = []
        route = Route('POST', f'/interactions/{self._interaction.id}/{self._interaction.token}/callback')

        payload: Dict[str, Any] = {'tts': tts}
        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed.to_dict()]
        if embeds:
            payload['embeds'] = [embed.to_dict() for embed in embeds]
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if view:
            payload['components'] = view.to_components()
        if ephemeral:
            payload['flags'] = 64
        if file:
            files = [file]
        if not files:
            files = []

        # handling non-attachment data
        form.append(
            {
                'name': 'payload_json',
                'value': json.dumps({
                    'type': 4,
                    'data': json.loads(_to_json(payload))
                })
            }
        )

        # handling attachment data
        if len(files) == 1:
            file = files[0]
            form.append(
                {
                    'name': 'file',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
        else:
            for index, file in enumerate(files):
                form.append(
                    {
                        'name': f'file{index}',
                        'value': file.fp,
                        'filename': file.filename,
                        'content_type': 'application/octet-stream',
                    }
                )
        await self._client.http.request(route, form=form, files=files)

    async def defer(self):
        route = Route('POST', f'/interactions/{self._interaction.id}/{self._interaction.token}/callback')
        return await self._client.http.request(route, json={'type': '5'})

    @property
    def followup(self):
        payload = {
            'id': self.application_id,
            'type': 3,
            'token': self._interaction.token,
        }
        return Webhook.from_state(data=payload, state=self._client._connection)

    @property
    def typing(self):
        return self.channel.typing
