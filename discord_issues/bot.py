import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv


# --- Basic Logging Setup ---
# This provides more detailed output than print() for debugging.
logging.basicConfig(level=logging.INFO)

# --- Load Environment Variables ---
# This loads the DISCORD_TOKEN from your .env file.
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


class IssueTrackerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        logging.info("Running setup hook...")

        # TODO: Figure out best way to set up db here

        # Load all command cogs from the cogs directory
        logging.info("Loading cogs...")
        for filename in os.listdir("./discord_issues/cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    cog_path = f"discord_issues.cogs.{filename[:-3]}"
                    await self.load_extension(cog_path)
                    logging.info(f"Successfully loaded cog: {cog_path}")
                except Exception as e:
                    logging.error(f"Failed to load cog {filename}: {e}")

        # Sync slash commands to Discord.
        # try:
        #     synced = await self.tree.sync()
        #     logging.info(f"Synced {len(synced)} application command(s).")
        # except Exception as e:
        #     logging.error(f"Failed to sync application commands: {e}")

    async def on_ready(self):
        if not self.user:
            logging.error("Bot user is not set. Exiting...")
            return
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logging.info("Bot is ready and online!")


async def main():
    """Main function to create and run the bot."""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set. Please check your .env file.")

    bot = IssueTrackerBot()
    await bot.start(DISCORD_TOKEN)
