import discord
import logging
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
            value=str(tag.name),
        )
        for tag in tags
        if current.lower() in tag.name.lower()
    ][:25]


class TagCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.project_repo = ProjectRepository()
        self.tag_repo = TagRepository()

    tag_group = app_commands.Group(name="tag", description="Commands for managing tags")

    @tag_group.command(name="new")
    @app_commands.autocomplete(project_name=project_autocomplete)
    async def new(
        self, interaction: discord.Interaction, project_name: str, tag_name: str
    ):
        await interaction.response.defer(ephemeral=True)

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.followup.send(f"❌ Project '{project_name}' not found.")
            return

        existing_tag = self.tag_repo.find_by_name(project.id, tag_name)
        if existing_tag:
            await interaction.followup.send(
                f"❌ A tag named '{tag_name}' already exists in project '{project_name}'."
            )
            return

        try:
            new_tag = self.tag_repo.create(name=tag_name, project_id=project.id)
            logging.info(
                f"Created new tag '{new_tag.name}' for project '{project.name}' in guild {interaction.guild_id}"
            )

            embed = discord.Embed(
                title="✅ Tag Created",
                description=f"Successfully created tag **{new_tag.name}** for project **{project.name}**.",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error creating tag: {e}")
            await interaction.followup.send(
                "❌ An unexpected error occurred while creating the tag."
            )

    @tag_group.command(
        name="list", description="Lists all tags for a specific project."
    )
    @app_commands.autocomplete(project_name=project_autocomplete)
    async def list_tags(self, interaction: discord.Interaction, project_name: str):
        """Handler for the /tag list command."""
        await interaction.response.defer(ephemeral=True)

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.followup.send(f"❌ Project '{project_name}' not found.")
            return

        tags = self.tag_repo.find_by_project_id(project.id)

        if not tags:
            embed = discord.Embed(
                title=f"Tags for {project.name}",
                description="This project has no tags yet.",
                color=discord.Color.blue(),
            )
        else:
            tag_list = "\n".join(f"- `{tag.name}`" for tag in tags)
            embed = discord.Embed(
                title=f"🏷️ Tags for {project.name}",
                description=tag_list,
                color=discord.Color.blue(),
            )

        await interaction.followup.send(embed=embed)

    @tag_group.command(name="delete", description="Deletes a tag from a project.")
    @app_commands.autocomplete(
        project_name=project_autocomplete, tag_name=tag_autocomplete
    )
    async def delete_tag(
        self, interaction: discord.Interaction, project_name: str, tag_name: str
    ):
        """Handler for the /tag delete command."""
        await interaction.response.defer(ephemeral=True)

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.followup.send(f"❌ Project '{project_name}' not found.")
            return

        tag_to_delete = self.tag_repo.find_by_name(project.id, tag_name)
        if not tag_to_delete:
            await interaction.followup.send(
                f"❌ Tag '{tag_name}' not found in project '{project_name}'."
            )
            return

        try:
            success = self.tag_repo.delete(pk=tag_to_delete.id)
            if success:
                logging.info(
                    f"Deleted tag '{tag_name}' from project '{project.name}' in guild {interaction.guild_id}"
                )
                embed = discord.Embed(
                    title="🗑️ Tag Deleted",
                    description=f"Successfully deleted tag **{tag_name}** from project **{project.name}**.",
                    color=discord.Color.orange(),
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Failed to delete the tag.")
        except Exception as e:
            logging.error(f"Error deleting tag: {e}")
            await interaction.followup.send(
                "❌ An unexpected error occurred. This tag might be in use by an issue."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(TagCog(bot))
