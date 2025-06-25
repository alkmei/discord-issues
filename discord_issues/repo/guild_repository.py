from discord_issues.db.models import Guild
from .base_repository import BaseRepository


class GuildRepository(BaseRepository[Guild]):
    def __init__(self):
        super().__init__(Guild)
