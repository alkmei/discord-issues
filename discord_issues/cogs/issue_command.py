import discord
from discord import app_commands
from discord.ext import commands


class IssueCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    issue_group = app_commands.Group(
        name="issue", description="Commands for managing issues"
    )

    @issue_group.command(name="new", description="Create a new issue")
    async def create(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ):
        await interaction.response.defer()
        await interaction.followup.send("Hello")


async def setup(bot: commands.Bot):
    await bot.add_cog(IssueCog(bot))
