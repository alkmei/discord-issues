import pytest_asyncio
import discord
from discord.ext import commands
import discord.ext.test as dpytest


@pytest_asyncio.fixture
async def bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="", intents=intents)
    await bot._async_setup_hook()
    dpytest.configure(bot)
    yield bot
    await dpytest.empty_queue()
