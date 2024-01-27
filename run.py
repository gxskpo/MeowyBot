from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

load_dotenv()


async def load_cogs():
    for i in os.listdir("cogs"):
        if i.endswith(".py"):
            await bot.load_extension(f"cogs.{i[:-3]}")
            print(f"Loaded {i[:-3]}")


@bot.event
async def on_ready():
    await load_cogs()
    print("Bot is ready!")


async def main():
    await bot.login(os.getenv("TOKEN"))
    await bot.connect()


if __name__ == "__main__":
    asyncio.run(main())
