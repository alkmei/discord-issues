import datetime
import enum
from typing import List, Optional

from sqlalchemy import (
    Column,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    DateTime,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class with naming convention for all models."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


issue_tags = Table(
    "issue_tags",
    Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

issue_assignees = Table(
    "issue_assignees",
    Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
)


class IssueStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


# --- Declarative Models ---
class Guild(Base):
    __tablename__ = "guilds"
    guild_id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    projects: Mapped[List["Project"]] = relationship(
        back_populates="guild", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    created_issues: Mapped[List["Issue"]] = relationship(
        foreign_keys="[Issue.creator_id]", back_populates="creator"
    )
    assigned_issues: Mapped[List["Issue"]] = relationship(
        secondary=issue_assignees, back_populates="assignees"
    )


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    guild_id: Mapped[str] = mapped_column(ForeignKey("guilds.guild_id"))
    guild: Mapped["Guild"] = relationship(back_populates="projects")

    issues: Mapped[List["Issue"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tags")
    issues: Mapped[List["Issue"]] = relationship(
        secondary=issue_tags, back_populates="tags"
    )


class Issue(Base):
    __tablename__ = "issues"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_issue_id: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[IssueStatus] = mapped_column(
        SQLAlchemyEnum(IssueStatus, name="issue_status_enum"),
        default=IssueStatus.OPEN,
        nullable=False,
    )

    creator_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    project: Mapped["Project"] = relationship(back_populates="issues")
    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id], back_populates="created_issues"
    )
    assignees: Mapped[List["User"]] = relationship(
        secondary=issue_assignees, back_populates="assigned_issues"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=issue_tags, back_populates="issues"
    )
