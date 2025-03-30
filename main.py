import os
import traceback

import discohook


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