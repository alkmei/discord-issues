import discord
from discord import app_commands
from discord.ext import commands
from ..repo.project_repository import ProjectRepository
from ..repo.tag_repository import TagRepository


async def project_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    project_repo = ProjectRepository()
    projects = project_repo.find_by_guild_id(str(interaction.guild_id))
    return [
        app_commands.Choice(name=str(project.name), value=str(project.name))
        for project in projects
        if current.lower() in project.name.lower()
    ][:25]


async def tag_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocompletes tag names based on the selected project."""
    project_name = interaction.namespace.project_name
    if not project_name:
        return []

    project_repo = ProjectRepository()
    tag_repo = TagRepository()

    project = project_repo.find_by_name(str(interaction.guild_id), project_name)
    if not project:
        return []

    tags = tag_repo.find_by_project_id(project.id)
    return [
        app_commands.Choice(
            name=tag.name,
            # CHANGED: Explicitly cast to str here as well.
            value=str(tag.name),
        )
        for tag in tags
        if current.lower() in tag.name.lower()
    ][:25]


class TagCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tag_group = app_commands.Group(name="tag", description="Commands for managing tags")

    @tag_group.command(name="new")
    async def new(self, interaction: discord.Interaction, title: str, description: str):
        await interaction.response.defer()
        await interaction.followup.send("Hello")


async def setup(bot: commands.Bot):
    await bot.add_cog(TagCog(bot))
