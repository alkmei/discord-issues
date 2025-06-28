from typing import Optional
from discord_issues.db.models import Project
from .base_repository import BaseRepository
from sqlalchemy.orm import joinedload


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def find_by_name(self, guild_id: str, name: str) -> Optional[Project]:
        """Finds a project within a guild by its name."""
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(guild_id=guild_id, name=name)
                .first()
            )

    def find_by_guild_id(self, guild_id: str) -> list[Project]:
        """Finds all projects associated with a specific guild ID."""
        with self.session_factory() as session:
            return (
                session.query(self.model).filter(self.model.guild_id == guild_id).all()
            )

    def find_by_name_with_statuses(self, guild_id: str, name: str) -> Optional[Project]:
        """
        Finds a project by name and eagerly loads its statuses relationship.
        """
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(self.model.statuses))
                .filter_by(guild_id=guild_id, name=name)
                .first()
            )
