import discord
from discord import app_commands
from discord.ext import commands


class TagCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tag_group = app_commands.Group(name="tag", description="Commands for managing tags")

    @tag_group.command(name="create")
    async def create(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ):
        await interaction.response.defer()
        await interaction.followup.send("Hello")


async def setup(bot: commands.Bot):
    await bot.add_cog(TagCog(bot))
