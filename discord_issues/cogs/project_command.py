import logging
from typing import Union
import discord
from discord import app_commands
from discord.ext import commands

from discord_issues.repo.guild_repository import GuildRepository
from discord_issues.repo.project_repository import ProjectRepository


async def project_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocompletes the project name for the current guild."""
    project_repo = ProjectRepository()
    projects = project_repo.find_by_guild_id(str(interaction.guild_id))
    return [
        app_commands.Choice(name=project.name, value=str(project.name))
        for project in projects
        if current.lower() in project.name.lower()
    ][:25]


class ConfirmDeleteView(discord.ui.View):
    """A view that provides confirmation buttons for a delete action."""

    def __init__(
        self,
        author: Union[discord.User, discord.Member],
        project_name: str,
        project_repo: ProjectRepository,
        project_id: int,
    ):
        super().__init__(timeout=60.0)
        self.author = author
        self.project_name = project_name
        self.project_repo = project_repo
        self.project_id = project_id
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensures only the original command author can interact with the view."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "You are not authorized to perform this action.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
    async def confirm_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        try:
            success = self.project_repo.delete(pk=self.project_id)
            if success:
                embed = discord.Embed(
                    title="🗑️ Project Deleted",
                    description=f"The project **{self.project_name}** and all its associated data have been permanently deleted.",
                    color=discord.Color.red(),
                )
                await interaction.response.edit_message(embed=embed, view=None)
            else:
                await interaction.response.edit_message(
                    content="❌ Failed to delete the project.", view=None
                )
        except Exception as e:
            logging.error(f"Error during project deletion: {e}")
            await interaction.response.edit_message(
                content="❌ An unexpected error occurred.", view=None
            )

        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Deletion cancelled.", view=None
        )
        self.stop()


class ProjectCog(commands.Cog):
    """A cog for managing projects."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.project_repo = ProjectRepository()
        self.guild_repo = GuildRepository()

    project_group = app_commands.Group(
        name="project", description="Commands for managing projects"
    )

    @project_group.command(
        name="new", description="Creates a new project in this server."
    )
    async def new_project(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str | None = None,
    ):
        """Handler for the /project new command."""
        await interaction.response.defer(ephemeral=True)
        guild_id_str = str(interaction.guild_id)

        # Ensure the guild exists in our database
        guild = self.guild_repo.get(guild_id_str)
        if not guild:
            guild = self.guild_repo.create(guild_id=guild_id_str)

        # Check for duplicate project name in this guild
        if self.project_repo.find_by_name(guild_id_str, name):
            await interaction.followup.send(
                f"❌ A project named '{name}' already exists in this server."
            )
            return

        try:
            new_project = self.project_repo.create(
                name=name, description=description, guild_id=guild_id_str
            )
            embed = discord.Embed(
                title="✅ Project Created",
                description=f"Successfully created project **{new_project.name}**.",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error creating project: {e}")
            await interaction.followup.send(
                "❌ An unexpected error occurred while creating the project."
            )

    @project_group.command(
        name="list", description="Lists all projects in this server."
    )
    async def list_projects(self, interaction: discord.Interaction):
        """Handler for the /project list command."""
        await interaction.response.defer(ephemeral=True)
        projects = self.project_repo.find_by_guild_id(str(interaction.guild_id))

        if not projects:
            await interaction.followup.send(
                "This server has no projects yet. Create one with `/project create`."
            )
            return

        embed = discord.Embed(
            title="Projects in this Server", color=discord.Color.blue()
        )
        for project in projects:
            desc = project.description or "No description provided."
            embed.add_field(name=f"📂 {project.name}", value=f"``````", inline=False)

        await interaction.followup.send(embed=embed)

    @project_group.command(
        name="edit", description="Edits the name or description of a project."
    )
    @app_commands.autocomplete(project_name=project_autocomplete)
    async def edit_project(
        self,
        interaction: discord.Interaction,
        project_name: str,
        new_name: str | None = None,
        new_description: str | None = None,
    ):
        """Handler for the /project edit command."""
        await interaction.response.defer(ephemeral=True)

        if not new_name and not new_description:
            await interaction.followup.send(
                "❌ You must provide a new name or a new description to edit."
            )
            return

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.followup.send(f"❌ Project '{project_name}' not found.")
            return

        update_data = {}
        if new_name:
            # Check for name collision
            if self.project_repo.find_by_name(str(interaction.guild_id), new_name):
                await interaction.followup.send(
                    f"❌ A project named '{new_name}' already exists."
                )
                return
            update_data["name"] = new_name
        if new_description:
            update_data["description"] = new_description

        try:
            self.project_repo.update(pk=project.id, **update_data)
            embed = discord.Embed(
                title="✅ Project Updated",
                description=f"Successfully updated project **{project_name}**.",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error updating project: {e}")
            await interaction.followup.send(
                "❌ An unexpected error occurred while updating the project."
            )

    @project_group.command(
        name="delete", description="Deletes a project and all of its data."
    )
    @app_commands.autocomplete(project_name=project_autocomplete)
    async def delete_project(self, interaction: discord.Interaction, project_name: str):
        """Handler for the /project delete command."""
        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.response.send_message(
                f"❌ Project '{project_name}' not found.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Confirm Deletion",
            description=(
                f"Are you sure you want to delete the project **{project.name}**?\n\n"
                "**This action is irreversible and will delete all associated issues, tags, and statuses.**"
            ),
            color=discord.Color.red(),
        )
        view = ConfirmDeleteView(
            interaction.user, project.name, self.project_repo, project.id
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    """The setup function to add the cog to the bot."""
    await bot.add_cog(ProjectCog(bot))
