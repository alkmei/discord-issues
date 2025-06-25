from .base_repository import BaseRepository
from discord_issues.db.models import Issue, User


class IssueRepository(BaseRepository[Issue]):
    def __init__(self):
        super().__init__(Issue)

    def find_open_issues_for_user(self, user: User) -> list[Issue]:
        """
        An example of a custom method that goes beyond basic CRUD.
        """
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(
                    self.model.assignees.contains(user), self.model.status == "Open"
                )
                .all()
            )
