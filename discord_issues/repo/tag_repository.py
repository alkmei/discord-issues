from typing import Optional
from discord_issues.db.models import Tag
from .base_repository import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)

    def find_by_project_id(self, project_id: int) -> list[Tag]:
        """Finds all tags belonging to a specific project."""
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.project_id == project_id)
                .all()
            )

    def find_by_name(self, project_id: int, name: str) -> Optional[Tag]:
        """Finds a tag within a project by its name."""
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(project_id=project_id, name=name)
                .first()
            )
