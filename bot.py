import interactions
import discord
from modules.chat_tools import *
import os
from io import BytesIO

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
VERSION="1.0.0"
NAME="Oscar"


bot = interactions.Client(token=DISCORD_TOKEN)



async def send_message_to_discord(ctx, text, image_url, image_descriptor, question_summary, max_chars=2000):
    await ctx.send(f"""**{question_summary}**\n*{image_descriptor}*""")
    if image_url is not None:
        await ctx.send(f"""{image_url}""")
    else:
        await ctx.send(f"""Image unable to be generated.""")
    #Split the message into chunks of max_chars
    for chunk in [text[i:i + max_chars] for i in range(0, len(text), max_chars)]:
        await ctx.send(chunk)

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(presence=interactions.ClientPresence(status='online', activities=[interactions.api.models.presence.PresenceActivity(type=0, name=f"{NAME} v{VERSION}")]))


@bot.command()
@interactions.option("question", description=f"Ask {NAME} something", type=interactions.OptionType.STRING, required=True)
async def ask(ctx: interactions.CommandContext, question: str):
    """Ask GPT-4 something"""
    await ctx.defer()
    print(f"Received question: {question}")
    await send_message_to_discord(ctx, *construct_answer(question))

#If DISCORD_TOKEN, OPENAI_API_KEY, and PERSONALITY are not set, quit
if DISCORD_TOKEN is None or OPENAI_API_KEY is None:
    print("DISCORD_TOKEN and OPENAI_API_KEY must be set as environment variables")
    quit()


bot.start()