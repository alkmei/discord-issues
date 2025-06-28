import logging
from typing import List, Any
import discord
from discord import app_commands
from discord.ext import commands

from ..repo.issue_repository import IssueRepository
from ..repo.project_repository import ProjectRepository
from ..repo.status_repository import StatusRepository
from ..repo.tag_repository import TagRepository
from ..repo.user_repository import UserRepository
from ..db.models import StatusCategory  # Import the enum

from .project_command import project_autocomplete
from .status_command import status_autocomplete


async def issue_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    project_name = interaction.namespace.project_name
    if not project_name:
        return []

    project_repo = ProjectRepository()
    project = project_repo.find_by_name(str(interaction.guild_id), project_name)
    if not project:
        return []

    # TODO: Use a repository method to fetch issues
    with IssueRepository().session_factory() as session:
        issues = (
            session.query(IssueRepository().model)
            .filter_by(project_id=project.id)
            .order_by(IssueRepository().model.project_issue_id.desc())
            .limit(25)
            .all()
        )

    choices = []
    for issue in issues:
        choice_name = f"#{issue.project_issue_id}: {issue.title}"
        if current.lower() in choice_name.lower():
            choices.append(
                app_commands.Choice(
                    name=choice_name[:100], value=issue.project_issue_id
                )
            )
    return choices


class IssueCreateModal(discord.ui.Modal, title="Create New Issue"):
    def __init__(self, issue_repo: IssueRepository, project, creator, initial_status):
        super().__init__()
        self.issue_repo = issue_repo
        self.project = project
        self.creator = creator
        self.initial_status = initial_status

    title_input = discord.ui.TextInput(
        label="Issue Title",
        placeholder="e.g., 'Website login button not working'",
        required=True,
        max_length=255,
    )
    description_input = discord.ui.TextInput(
        label="Description",
        placeholder="Provide a detailed description of the issue. Include steps to reproduce if applicable.",
        style=discord.TextStyle.paragraph,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            issue = self.issue_repo.create_issue(
                project=self.project,
                creator=self.creator,
                title=self.title_input.value,
                description=self.description_input.value,
                initial_status=self.initial_status,
            )
            embed = discord.Embed(
                title=f"✅ Issue Created: #{issue.project_issue_id}",
                description=f"Successfully created a new issue in project **{self.project.name}**.",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error creating issue via modal: {e}")
            await interaction.followup.send(
                "❌ An unexpected error occurred while creating the issue."
            )


class IssueCog(commands.Cog):
    """A cog for all commands related to creating and managing issues."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.issue_repo = IssueRepository()
        self.project_repo = ProjectRepository()
        self.user_repo = UserRepository()
        self.tag_repo = TagRepository()
        self.status_repo = StatusRepository()

    issue_group = app_commands.Group(
        name="issue", description="Commands for managing issues"
    )

    @issue_group.command(name="create", description="Creates a new issue in a project.")
    @app_commands.autocomplete(project_name=project_autocomplete)
    async def create_issue(self, interaction: discord.Interaction, project_name: str):
        """Opens a modal to create a new issue."""
        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.response.send_message(
                f"❌ Project '{project_name}' not found.", ephemeral=True
            )
            return

        creator = self.user_repo.get(str(interaction.user.id))
        if not creator:
            creator = self.user_repo.create(user_id=str(interaction.user.id))

        # Find the default "OPEN" status for the project
        initial_status = next(
            (s for s in project.statuses if s.category == StatusCategory.OPEN), None
        )
        if not initial_status:
            await interaction.response.send_message(
                "❌ This project has no default 'OPEN' status configured. "
                "An administrator must create one with `/status create`.",
                ephemeral=True,
            )
            return

        modal = IssueCreateModal(self.issue_repo, project, creator, initial_status)
        await interaction.response.send_modal(modal)

    @issue_group.command(
        name="view", description="Views the details of a specific issue."
    )
    @app_commands.autocomplete(
        project_name=project_autocomplete, issue_id=issue_autocomplete
    )
    async def view_issue(
        self, interaction: discord.Interaction, project_name: str, issue_id: int
    ):
        """Displays a detailed embed for a single issue."""
        await interaction.response.defer()

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            await interaction.followup.send(
                f"❌ Project '{project_name}' not found.", ephemeral=True
            )
            return

        issue = self.issue_repo.find_by_project_issue_id(project.id, issue_id)
        if not issue:
            await interaction.followup.send(
                f"❌ Issue #{issue_id} not found in project '{project_name}'.",
                ephemeral=True,
            )
            return

        color = (
            discord.Color.green()
            if issue.status.category == StatusCategory.CLOSED
            else discord.Color.red()
        )
        embed = discord.Embed(
            title=f"[{project.name}] Issue #{issue.project_issue_id}: {issue.title}",
            description=issue.description or "No description provided.",
            color=color,
            timestamp=issue.created_at,
        )

        creator_user = await self.bot.fetch_user(int(issue.creator_id))

        embed.add_field(name="Status", value=f"`{issue.status.name}`", inline=True)
        embed.add_field(name="Creator", value=creator_user.mention, inline=True)

        assignees_str = (
            ", ".join([f"<@{assignee.user_id}>" for assignee in issue.assignees])
            or "None"
        )
        embed.add_field(name="Assignees", value=assignees_str, inline=False)

        tags_str = ", ".join([f"`{tag.name}`" for tag in issue.tags]) or "None"
        embed.add_field(name="Tags", value=tags_str, inline=False)

        embed.set_footer(text=f"Last updated")
        embed.timestamp = issue.updated_at

        await interaction.followup.send(embed=embed)

    @issue_group.command(name="assign", description="Assigns a user to an issue.")
    @app_commands.autocomplete(
        project_name=project_autocomplete, issue_id=issue_autocomplete
    )
    async def assign_issue(
        self,
        interaction: discord.Interaction,
        project_name: str,
        issue_id: int,
        user: discord.User,
    ):
        """Assigns a user to an issue."""
        await interaction.response.defer(ephemeral=True)

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            return await interaction.followup.send(
                f"❌ Project '{project_name}' not found."
            )

        issue = self.issue_repo.find_by_project_issue_id(project.id, issue_id)
        if not issue:
            return await interaction.followup.send(f"❌ Issue #{issue_id} not found.")

        # Get or create the user in our database
        db_user = self.user_repo.get(str(user.id))
        if not db_user:
            db_user = self.user_repo.create(user_id=str(user.id))

        if db_user in issue.assignees:
            return await interaction.followup.send(
                f"{user.mention} is already assigned to issue #{issue.project_issue_id}."
            )

        with self.issue_repo.session_factory() as session:
            with session.begin():
                # Re-fetch the issue within the session to modify its relationships
                session_issue = session.get(self.issue_repo.model, issue.id)
                if not session_issue:
                    return await interaction.followup.send(
                        f"❌ Issue #{issue_id} not found in the database."
                    )
                session_issue.assignees.append(db_user)

        await interaction.followup.send(
            f"✅ Assigned {user.mention} to issue #{issue.project_issue_id}."
        )

    @issue_group.command(name="status", description="Changes the status of an issue.")
    @app_commands.autocomplete(
        project_name=project_autocomplete,
        issue_id=issue_autocomplete,
        status_name=status_autocomplete,
    )
    async def status_issue(
        self,
        interaction: discord.Interaction,
        project_name: str,
        issue_id: int,
        status_name: str,
    ):
        """Changes an issue's status."""
        await interaction.response.defer(ephemeral=True)

        project = self.project_repo.find_by_name(
            str(interaction.guild_id), project_name
        )
        if not project:
            return await interaction.followup.send(
                f"❌ Project '{project_name}' not found."
            )

        issue = self.issue_repo.find_by_project_issue_id(project.id, issue_id)
        if not issue:
            return await interaction.followup.send(f"❌ Issue #{issue_id} not found.")

        new_status = self.status_repo.find_by_name(project.id, status_name)
        if not new_status:
            return await interaction.followup.send(
                f"❌ Status '{status_name}' not found."
            )

        update_data: dict[str, Any] = {"status_id": new_status.id}
        # If the new status is a closing status, record the close time
        if new_status.category == StatusCategory.CLOSED and not issue.closed_at:
            update_data["closed_at"] = discord.utils.utcnow()
        # If we're reopening an issue, clear the close time
        elif new_status.category == StatusCategory.OPEN and issue.closed_at:
            update_data["closed_at"] = None

        self.issue_repo.update(pk=issue.id, **update_data)

        await interaction.followup.send(
            f"✅ Issue #{issue.project_issue_id} status changed to **{status_name}**."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(IssueCog(bot))
