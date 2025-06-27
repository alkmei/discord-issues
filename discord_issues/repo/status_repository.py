from typing import Optional
from discord_issues.db.models import Project
from .base_repository import BaseRepository


class StatusRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def find_by_project_id(self, project_id: int) -> list[Project]:
        """
        Find all statuses associated with a specific project ID.

        :param project_id: The ID of the project to find statuses for.
        :return: A list of Project objects associated with the given project ID.
        """
        with self.session_factory() as session:
            return session.query(self.model).filter_by(project_id=project_id).all()
