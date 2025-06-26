import discord
from discord import app_commands
from discord.ext import commands


class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    Status_group = app_commands.Group(
        name="Status", description="Commands for managing status"
    )

    @Status_group.command(name="create", description="Create a new status")
    async def create(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ):
        await interaction.response.defer()
        await interaction.followup.send("Hello")


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
