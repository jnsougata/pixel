import os
import traceback
from typing import Optional

import discohook
from google import genai
from google.genai import types

ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = discohook.Client(
    application_id=os.getenv("APPLICATION_ID"),
    public_key=os.getenv("PUBLIC_KEY"),
    token=os.getenv("DISCORD_TOKEN"),
    password=os.getenv("APPLICATION_PASSWORD"),
)


@app.on_interaction_error()
async def on_error(e: discohook.InteractionException):
    embed = discohook.Embed(
        title='Oops!',
        description=f'Something went wrong!'
                    f'\nTrying again might fix it.'
                    f'\nIf not, please contact the developer.'
                    f'\n\nTo Join Development Server [Click Here](https://discord.gg/ChJbUv7z8V)',
        color=0xff0000
    )
    if e.interaction.responded:
        await e.interaction.response.followup(embed=embed, ephemeral=True)
    else:
        await e.interaction.response.send(embed=embed, ephemeral=True)
    err = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    embed = discohook.Embed(
        title='Stack Trace',
        description=f'```py\n{err}\n```',
        color=0xff0000
    )
    await app.send(os.getenv("LOG_CHANNEL_ID"), embed=embed)

@app.load
@discohook.command.slash("ping")
async def ping(i: discohook.Interaction):
    """Ping Pong"""
    await i.response.send("Pong!")

@app.load
@discohook.command.slash("ask", description="ask a question", options=[
    discohook.Option(
        name="question",
        description="Question to ask",
        kind=discohook.ApplicationCommandOptionType.string,
        required=True
    ),
    discohook.Option(
        name="attachment",
        description="Attachment to ask a question about",
        kind=discohook.ApplicationCommandOptionType.attachment,
        required=False
    )
])
async def ask(i: discohook.Interaction, question: str, attachment: Optional[discohook.Attachment] = None):
    await i.response.defer()
    contents = [f"{question}\n\n respond in about 2000 characters. Use simple markdown formatting."]
    if attachment is not None:
        content_bytes = await attachment.read()
        contents.append(
            types.Part.from_bytes(
                data=content_bytes,
                mime_type=attachment.content_type,
            )
        )
    response = ai.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents
    )
    await i.response.followup(response.text)

@app.load
@discohook.command.message("translate")
async def translate(i: discohook.Interaction, message: discohook.Message):
    await i.response.defer(ephemeral=True)

    text = f"Translate `{message.content}` to english. Respond with only the translation."
    response = ai.models.generate_content(
        model="gemini-2.0-flash",
        contents=[text]
    )
    await i.response.followup(response.text, ephemeral=True)