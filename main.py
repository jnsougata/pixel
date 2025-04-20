import contextlib
import os
import traceback
from typing import Optional

import discohook
from dotenv import load_dotenv
from google import genai
from google.genai import types
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

load_dotenv()


@contextlib.asynccontextmanager
async def lifespan(client: discohook.Client):
    try:
        yield
    finally:
        if client.http.session:
            await client.http.session.close()


ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = discohook.Client(
    application_id=os.getenv("APPLICATION_ID"),
    public_key=os.getenv("PUBLIC_KEY"),
    token=os.getenv("DISCORD_TOKEN"),
    password=os.getenv("APPLICATION_PASSWORD"),
    default_help_command=True,
)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


async def homepage(_request):
    return FileResponse("index.html", media_type="text/html")


app.add_route(path="/", methods=["GET"], route=homepage)


@app.on_interaction_error()
async def on_error(e: discohook.InteractionException):
    embed = discohook.Embed(
        title="Oops!",
        description=f"Something went wrong!"
        f"\nTrying again might fix it."
        f"\nIf not, please contact the developer."
        f"\n\nTo Join Development Server [Click Here](https://discord.gg/ChJbUv7z8V)",
        color=0xFF0000,
    )
    if e.interaction.responded:
        await e.interaction.response.followup(embed=embed, ephemeral=True)
    else:
        await e.interaction.response.send(embed=embed, ephemeral=True)
    err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    embed = discohook.Embed(
        title="Stack Trace", description=f"```py\n{err}\n```", color=0xFF0000
    )
    await app.send(os.getenv("LOG_CHANNEL_ID"), embed=embed)


@app.load
@discohook.command.slash("ping")
async def ping(i: discohook.Interaction):
    """Ping Pong"""
    await i.response.send("Pong!")


@app.load
@discohook.command.slash(
    "ask",
    description="Ask a question",
    options=[
        discohook.Option(
            name="prompt",
            description="Question to ask",
            kind=discohook.ApplicationCommandOptionType.string,
            required=True,
        ),
        discohook.Option(
            name="attachment",
            description="Attachment to ask a question about",
            kind=discohook.ApplicationCommandOptionType.attachment,
            required=False,
        ),
    ],
    contexts=[
        discohook.InteractionContextType.guild,
        discohook.InteractionContextType.bot_dm,
        discohook.InteractionContextType.private_channel,
    ],
)
async def ask(
    i: discohook.Interaction,
    prompt: str,
    attachment: Optional[discohook.Attachment] = None,
):
    await i.response.defer()
    contents = [
        f"{prompt}\n\n respond in about 2000 characters. Use simple markdown formatting."
    ]
    if attachment is not None:
        content_bytes = await attachment.read()
        contents.append(
            types.Part.from_bytes(
                data=content_bytes,
                mime_type=attachment.content_type,
            )
        )
    response = ai.models.generate_content(model="gemini-2.0-flash", contents=contents)
    await i.response.followup(response.text)


@app.load
@discohook.command.message(
    "translate",
    contexts=[
        discohook.InteractionContextType.guild,
        discohook.InteractionContextType.bot_dm,
        discohook.InteractionContextType.private_channel,
    ],
)
async def translate(i: discohook.Interaction, message: discohook.Message):
    await i.response.defer(ephemeral=True)

    text = (
        f"Translate `{message.content}` to english. Respond with only the translation."
    )
    response = ai.models.generate_content(
        model="gemini-2.0-flash",
        contents=[text],
        config=types.GenerateContentConfig(response_modalities=["Text"]),
    )
    await i.response.followup(response.text, ephemeral=True)


@app.load
@discohook.command.slash(
    "imagine",
    description="Generate an image based on a prompt",
    options=[
        discohook.Option(
            name="prompt",
            description="Prompt to generate an image from",
            kind=discohook.ApplicationCommandOptionType.string,
            required=True,
        ),
        discohook.Option(
            name="attachment",
            description="Attachment to generate an image from",
            kind=discohook.ApplicationCommandOptionType.attachment,
            required=False,
        ),
    ],
    contexts=[
        discohook.InteractionContextType.guild,
        discohook.InteractionContextType.bot_dm,
        discohook.InteractionContextType.private_channel,
    ],
)
async def imagine(
    i: discohook.Interaction,
    prompt: str,
    attachment: Optional[discohook.Attachment] = None,
):
    await i.response.defer()
    contents = [prompt]
    if attachment is not None:
        content_bytes = await attachment.read()
        contents.append(
            types.Part.from_bytes(
                data=content_bytes,
                mime_type=attachment.content_type,
            )
        )
    response = ai.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["Image", "Text"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            continue
        elif part.inline_data is not None:
            file = discohook.File(
                name="imagine.png",
                content=part.inline_data.data,
                description="Generated by Gemini",
            )
            embed = discohook.Embed(
                title="Generated Image",
                description=f"` Prompt ` {prompt}",
            )
            embed.set_image(file)
            await i.response.followup(embed=embed)
            return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
