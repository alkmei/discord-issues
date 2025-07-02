import pytest
from unittest.mock import MagicMock, AsyncMock
from discord import app_commands

from discord_issues.cogs.project_command import project_autocomplete
from discord_issues.cogs.project_command import ProjectCog


@pytest.mark.asyncio
async def test_project_autocomplete_returns_matching_projects(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123

    MockProjectRepo = mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    )
    mock_project1 = MagicMock()
    mock_project1.name = "Alpha"
    mock_project2 = MagicMock()
    mock_project2.name = "Beta"
    MockProjectRepo.return_value.find_by_guild_id.return_value = [
        mock_project1,
        mock_project2,
    ]

    results = await project_autocomplete(mock_interaction, "a")
    assert len(results) == 2
    assert all(isinstance(choice, app_commands.Choice) for choice in results)
    assert {c.name for c in results} == {"Alpha", "Beta"}


@pytest.mark.asyncio
async def test_new_project_duplicate_name(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch guild repo
    mocker.patch(
        "discord_issues.cogs.project_command.GuildRepository"
    ).return_value.get.return_value = MagicMock()
    # Patch project repo: find_by_name returns a project (duplicate)
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = MagicMock()

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.new_project.callback(cog, mock_interaction, "Alpha", "desc")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ A project named 'Alpha' already exists in this server."
    )


@pytest.mark.asyncio
async def test_new_project_success(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch guild repo
    mocker.patch(
        "discord_issues.cogs.project_command.GuildRepository"
    ).return_value.get.return_value = MagicMock()
    # Patch project repo: find_by_name returns None (no duplicate)
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None
    # Patch project repo: create returns a new project
    mock_new_project = MagicMock()
    mock_new_project.name = "Alpha"
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.create.return_value = mock_new_project

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.new_project.callback(cog, mock_interaction, "Alpha", "desc")

    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "✅ Project Created"
    assert "Alpha" in embed.description


@pytest.mark.asyncio
async def test_new_project_exception(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch guild repo
    mocker.patch(
        "discord_issues.cogs.project_command.GuildRepository"
    ).return_value.get.return_value = MagicMock()
    # Patch project repo: find_by_name returns None (no duplicate)
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None
    # Patch project repo: create raises exception
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.create.side_effect = Exception("DB error")

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.new_project.callback(cog, mock_interaction, "Alpha", "desc")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ An unexpected error occurred while creating the project."
    )


@pytest.mark.asyncio
async def test_list_projects_none(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch project repo: find_by_guild_id returns empty list
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_guild_id.return_value = []

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.list_projects.callback(cog, mock_interaction)

    mock_interaction.followup.send.assert_called_once_with(
        "This server has no projects yet. Create one with `/project create`."
    )


@pytest.mark.asyncio
async def test_list_projects_some(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch project repo: find_by_guild_id returns projects
    mock_project1 = MagicMock()
    mock_project1.name = "Alpha"
    mock_project1.description = "Desc1"
    mock_project2 = MagicMock()
    mock_project2.name = "Beta"
    mock_project2.description = None
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_guild_id.return_value = [mock_project1, mock_project2]

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.list_projects.callback(cog, mock_interaction)

    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "Projects in this Server"
    assert "Alpha" in embed.fields[0].name
    assert "Desc1" in embed.fields[0].value
    assert "Beta" in embed.fields[1].name
    assert "No description provided." in embed.fields[1].value


@pytest.mark.asyncio
async def test_edit_project_no_changes(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.edit_project.callback(cog, mock_interaction, "Alpha", None, None)
    mock_interaction.followup.send.assert_called_once_with(
        "❌ You must provide a new name or a new description to edit."
    )


@pytest.mark.asyncio
async def test_edit_project_not_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.edit_project.callback(cog, mock_interaction, "Alpha", "NewAlpha", None)
    mock_interaction.followup.send.assert_called_once_with(
        "❌ Project 'Alpha' not found."
    )


@pytest.mark.asyncio
async def test_edit_project_name_collision(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # First find_by_name returns the project to edit, second returns a collision
    mock_project = MagicMock()
    mock_project.id = 1
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.side_effect = [mock_project, MagicMock()]

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.edit_project.callback(cog, mock_interaction, "Alpha", "Beta", None)
    mock_interaction.followup.send.assert_called_once_with(
        "❌ A project named 'Beta' already exists."
    )


@pytest.mark.asyncio
async def test_edit_project_success(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.side_effect = [mock_project, None]
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.update.return_value = None

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.edit_project.callback(cog, mock_interaction, "Alpha", "Beta", "desc2")
    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "✅ Project Updated"
    assert "Alpha" in embed.description


@pytest.mark.asyncio
async def test_edit_project_exception(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.side_effect = [mock_project, None]
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.update.side_effect = Exception("DB error")

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.edit_project.callback(cog, mock_interaction, "Alpha", "Beta", "desc2")
    mock_interaction.followup.send.assert_called_once_with(
        "❌ A project named 'Beta' already exists."
    )


@pytest.mark.asyncio
async def test_delete_project_not_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.send_message = AsyncMock()

    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.delete_project.callback(cog, mock_interaction, "Alpha")
    mock_interaction.response.send_message.assert_called_once_with(
        "❌ Project 'Alpha' not found.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_delete_project_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.user = MagicMock()
    mock_interaction.response.send_message = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "Alpha"
    mocker.patch(
        "discord_issues.cogs.project_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project

    bot = MagicMock()
    cog = ProjectCog(bot)
    await cog.delete_project.callback(cog, mock_interaction, "Alpha")
    mock_interaction.response.send_message.assert_called_once()
    args, kwargs = mock_interaction.response.send_message.call_args
    embed = kwargs.get("embed")
    view = kwargs.get("view")
    assert embed.title == "⚠️ Confirm Deletion"
    assert "Alpha" in embed.description
    assert view is not None
