import discord
from discord import app_commands
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    admin_group = app_commands.Group(
        name="admin", description="Commands for managing admin stuff"
    )

    @admin_group.command(name="sync", description="Sync tree commands for development")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        await self.bot.tree.sync(guild=interaction.guild)
        await interaction.followup.send("Command tree synced.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
