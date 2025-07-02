import pytest
from discord import app_commands
from unittest.mock import MagicMock, AsyncMock

from discord_issues.cogs.tag_command import (
    tag_autocomplete,
    TagCog,
)


@pytest.mark.asyncio
async def test_tag_autocomplete_returns_tags(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 42
    mock_namespace = MagicMock()
    mock_namespace.project_name = "TestProject"
    mock_interaction.namespace = mock_namespace

    mock_project_repo = mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    )
    mock_tag_repo = mocker.patch("discord_issues.cogs.tag_command.TagRepository")

    mock_project = MagicMock()
    mock_project.id = 99
    mock_project_repo.return_value.find_by_name.return_value = mock_project

    mock_tag1 = MagicMock()
    mock_tag1.name = "AlphaTag"
    mock_tag2 = MagicMock()
    mock_tag2.name = "BetaTag"
    mock_tag3 = MagicMock()
    mock_tag3.name = "Irrelevant"
    mock_tag_repo.return_value.find_by_project_id.return_value = [
        mock_tag1,
        mock_tag2,
        mock_tag3,
    ]

    # Call the autocomplete with a search string that matches both tags
    results = await tag_autocomplete(mock_interaction, "tag")

    # Assertions
    assert len(results) == 2
    assert all(isinstance(choice, app_commands.Choice) for choice in results)
    assert {c.name for c in results} == {"AlphaTag", "BetaTag"}


@pytest.mark.asyncio
async def test_tag_new_creates_tag(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project_repo = mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    )
    mock_tag_repo = mocker.patch("discord_issues.cogs.tag_command.TagRepository")

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mock_project_repo.return_value.find_by_name.return_value = mock_project

    mock_tag_repo.return_value.find_by_name.return_value = None  # No existing tag

    mock_new_tag = MagicMock()
    mock_new_tag.name = "TagA"
    mock_tag_repo.return_value.create.return_value = mock_new_tag

    bot = MagicMock()
    cog = TagCog(bot)

    await cog.new.callback(cog, mock_interaction, "TestProject", "TagA")

    mock_interaction.followup.send.assert_called()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed is not None
    assert embed.title == "✅ Tag Created"
    assert "TagA" in embed.description
    assert "TestProject" in embed.description


@pytest.mark.asyncio
async def test_list_tags_project_not_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Patch repositories
    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None
    mocker.patch("discord_issues.cogs.tag_command.TagRepository")

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.list_tags.callback(cog, mock_interaction, "NoProject")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ Project 'NoProject' not found."
    )


@pytest.mark.asyncio
async def test_list_tags_no_tags(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    # Mock project and tag repo
    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_project_id.return_value = []

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.list_tags.callback(cog, mock_interaction, "TestProject")

    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "Tags for TestProject"
    assert "no tags yet" in embed.description


@pytest.mark.asyncio
async def test_list_tags_with_tags(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mock_tag1 = MagicMock()
    mock_tag1.name = "Alpha"
    mock_tag2 = MagicMock()
    mock_tag2.name = "Beta"

    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_project_id.return_value = [mock_tag1, mock_tag2]

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.list_tags.callback(cog, mock_interaction, "TestProject")

    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "🏷️ Tags for TestProject"
    assert "- `Alpha`" in embed.description
    assert "- `Beta`" in embed.description


@pytest.mark.asyncio
async def test_delete_tag_project_not_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = None
    mocker.patch("discord_issues.cogs.tag_command.TagRepository")

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.delete_tag.callback(cog, mock_interaction, "NoProject", "SomeTag")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ Project 'NoProject' not found."
    )


@pytest.mark.asyncio
async def test_delete_tag_tag_not_found(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_name.return_value = None

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.delete_tag.callback(cog, mock_interaction, "TestProject", "NoTag")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ Tag 'NoTag' not found in project 'TestProject'."
    )


@pytest.mark.asyncio
async def test_delete_tag_success(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mock_tag = MagicMock()
    mock_tag.id = 2
    mock_tag.name = "Alpha"

    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_name.return_value = mock_tag
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.delete.return_value = True

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.delete_tag.callback(cog, mock_interaction, "TestProject", "Alpha")

    mock_interaction.followup.send.assert_called_once()
    args, kwargs = mock_interaction.followup.send.call_args
    embed = kwargs.get("embed")
    assert embed.title == "🗑️ Tag Deleted"
    assert "Alpha" in embed.description
    assert "TestProject" in embed.description


@pytest.mark.asyncio
async def test_delete_tag_delete_failed(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mock_tag = MagicMock()
    mock_tag.id = 2
    mock_tag.name = "Alpha"

    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_name.return_value = mock_tag
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.delete.return_value = False

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.delete_tag.callback(cog, mock_interaction, "TestProject", "Alpha")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ Failed to delete the tag."
    )


@pytest.mark.asyncio
async def test_delete_tag_exception(mocker):
    mock_interaction = MagicMock()
    mock_interaction.guild_id = 123
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()

    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "TestProject"
    mock_tag = MagicMock()
    mock_tag.id = 2
    mock_tag.name = "Alpha"

    mocker.patch(
        "discord_issues.cogs.tag_command.ProjectRepository"
    ).return_value.find_by_name.return_value = mock_project
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.find_by_name.return_value = mock_tag
    mocker.patch(
        "discord_issues.cogs.tag_command.TagRepository"
    ).return_value.delete.side_effect = Exception("DB error")

    bot = MagicMock()
    cog = TagCog(bot)
    await cog.delete_tag.callback(cog, mock_interaction, "TestProject", "Alpha")

    mock_interaction.followup.send.assert_called_once_with(
        "❌ An unexpected error occurred. This tag might be in use by an issue."
    )
