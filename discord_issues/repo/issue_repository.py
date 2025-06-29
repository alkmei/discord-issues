from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from discord_issues.db.models import Issue, Project, Tag, User, IssueStatus
from .base_repository import BaseRepository


class IssueRepository(BaseRepository[Issue]):
    def __init__(self):
        super().__init__(Issue)

    def get_next_project_issue_id(self, project_id: int, session) -> int:
        """
        Calculates the next available issue ID for a given project.
        This should be called within an active session.
        """
        max_id = (
            session.query(func.max(self.model.project_issue_id))
            .filter(self.model.project_id == project_id)
            .scalar()
        )
        return (max_id or 0) + 1

    def find_by_project_issue_id(
        self, project_id: int, project_issue_id: int
    ) -> Optional[Issue]:
        """
        Finds a single issue by its user-facing ID within a specific project.
        e.g., finds issue #12 in project with id=1.
        """
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(
                    joinedload(self.model.assignees),
                    joinedload(self.model.tags),
                    joinedload(self.model.creator),
                )
                .filter_by(project_id=project_id, project_issue_id=project_issue_id)
                .first()
            )

    def create_issue(
        self,
        project: Project,
        creator: User,
        title: str,
        description: str,
        assignees: list[User] = [],
        tags: list[Tag] = [],
    ) -> Issue:
        """
        Creates a new issue and handles all its relationships.
        """
        with self.session_factory() as session:
            with session.begin():
                next_id = self.get_next_project_issue_id(project.id, session)

                new_issue = Issue(
                    project_issue_id=next_id,
                    title=title,
                    description=description,
                    project_id=project.id,
                    creator_id=creator.user_id,
                    status=IssueStatus.OPEN,
                )

                if assignees:
                    new_issue.assignees.extend(assignees)

                if tags:
                    new_issue.tags.extend(tags)

                session.add(new_issue)

            session.refresh(new_issue)
            return new_issue
