from typing import List
import discord
from discord import app_commands
from discord.ext import commands

from discord_issues.repo.project_repository import ProjectRepository
from discord_issues.repo.status_repository import StatusRepository


async def status_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    project_name = interaction.namespace.project_name
    if not project_name:
        return []

    project = ProjectRepository().find_by_name(str(interaction.guild_id), project_name)
    if not project:
        return []

    statuses = StatusRepository().find_by_project_id(project.id)
    return [
        app_commands.Choice(name=status.name, value=str(status.name))
        for status in statuses
        if current.lower() in status.name.lower()
    ][:25]


class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    status_group = app_commands.Group(
        name="status", description="Commands for managing status"
    )

    @status_group.command(name="new", description="Create a new status")
    async def create(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ):
        await interaction.response.defer()
        await interaction.followup.send("Hello")


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
