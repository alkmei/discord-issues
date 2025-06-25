from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Table,
    Text,
    MetaData,
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
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
    Column("user_id", String, ForeignKey("users.user_id"), primary_key=True),
)


class Guild(Base):
    __tablename__ = "guilds"
    guild_id = Column(String, primary_key=True, autoincrement=False)

    projects = relationship(
        "Project", back_populates="guild", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, autoincrement=False)

    created_issues = relationship(
        "Issue", foreign_keys="[Issue.creator_id]", back_populates="creator"
    )
    assigned_issues = relationship(
        "Issue", secondary=issue_assignees, back_populates="assignees"
    )


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    guild_id = Column(String, ForeignKey("guilds.guild_id"), nullable=False)
    guild = relationship("Guild", back_populates="projects")

    # A project is the new parent for issues, tags, and statuses
    issues = relationship(
        "Issue", back_populates="project", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", back_populates="project", cascade="all, delete-orphan")
    statuses = relationship(
        "Status", back_populates="project", cascade="all, delete-orphan"
    )


class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(
        Enum("OPEN", "CLOSED", name="status_category_enum"), nullable=False
    )

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="statuses")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="tags")
    issues = relationship("Issue", secondary=issue_tags, back_populates="tags")


class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    project_issue_id = Column(Integer, nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="issues")
    creator = relationship(
        "User", foreign_keys=creator_id, back_populates="created_issues"
    )

    status = relationship("Status")
    assignees = relationship(
        "User", secondary=issue_assignees, back_populates="assigned_issues"
    )
    tags = relationship("Tag", secondary=issue_tags, back_populates="issues")
