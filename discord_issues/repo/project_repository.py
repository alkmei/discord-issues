from typing import Optional
from discord_issues.db.models import Project, Status, StatusCategory
from .base_repository import BaseRepository
from sqlalchemy.orm import joinedload
import logging


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def create(self, **kwargs) -> Project:
        """
        Creates a new project and seeds it with a default set of statuses.
        """
        with self.session_factory() as session:
            with session.begin():  # Use session.begin() for an atomic transaction
                # Create the project instance
                new_project = self.model(**kwargs)
                session.add(new_project)

                # After adding, flush the session to assign an ID to new_project
                # without committing the transaction.
                session.flush()

                # Define the default statuses
                default_statuses = [
                    Status(
                        name="Open",
                        description="The issue is open and ready to be worked on.",
                        category=StatusCategory.OPEN,
                        project_id=new_project.id,
                    ),
                    Status(
                        name="In Progress",
                        description="The issue is actively being worked on.",
                        category=StatusCategory.OPEN,
                        project_id=new_project.id,
                    ),
                    Status(
                        name="Resolved",
                        description="The work is complete and the issue is resolved.",
                        category=StatusCategory.CLOSED,
                        project_id=new_project.id,
                    ),
                    Status(
                        name="Closed",
                        description="The issue has been formally closed.",
                        category=StatusCategory.CLOSED,
                        project_id=new_project.id,
                    ),
                ]

                session.add_all(default_statuses)
                logging.info(
                    f"Seeded {len(default_statuses)} default statuses for new project '{new_project.name}'."
                )

            session.refresh(new_project)
            return new_project

    def find_by_name(self, guild_id: str, name: str) -> Optional[Project]:
        """Finds a project within a guild by its name."""
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(self.model.statuses))
                .filter_by(guild_id=guild_id, name=name)
                .first()
            )

    def find_by_guild_id(self, guild_id: str) -> list[Project]:
        """Finds all projects associated with a specific guild ID."""
        with self.session_factory() as session:
            return (
                session.query(self.model).filter(self.model.guild_id == guild_id).all()
            )
