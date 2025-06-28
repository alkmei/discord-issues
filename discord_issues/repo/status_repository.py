from typing import Optional
from discord_issues.db.models import Status
from .base_repository import BaseRepository


class StatusRepository(BaseRepository[Status]):
    def __init__(self):
        super().__init__(Status)

    def find_by_project_id(self, project_id: int) -> list[Status]:
        """
        Find all statuses associated with a specific project ID.

        :param project_id: The ID of the project to find statuses for.
        :return: A list of Project objects associated with the given project ID.
        """
        with self.session_factory() as session:
            return session.query(self.model).filter_by(project_id=project_id).all()

    def find_by_name(self, project_id: int, name: str) -> Optional[Status]:
        """
        Find a status by its name and project ID.

        :param project_id: The ID of the project to which the status belongs.
        :param name: The name of the status to find.
        :return: An optional Project object if found, otherwise None.
        """
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(project_id=project_id, name=name)
                .first()
            )
