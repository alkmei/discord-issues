from typing import TypeVar, Type, Generic, Optional, Any
from discord_issues.db.database import SessionLocal
from discord_issues.db.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    A generic base repository that provides basic CRUD (Create, Read, Update, Delete)
    functionality for a given SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initializes the repository with a specific SQLAlchemy model.

        Args:
            model: The SQLAlchemy model class (e.g., Issue, User).
        """
        self.model = model
        self.session_factory = SessionLocal

    def get(self, pk: Any) -> Optional[ModelType]:
        """
        Retrieves a single record by its primary key.

        Args:
            pk: The primary key of the record to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        with self.session_factory() as session:
            return session.query(self.model).get(pk)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Retrieves all records, with optional pagination.

        Args:
            skip (int): The number of records to skip from the beginning.
            limit (int): The maximum number of records to return.

        Returns:
            A list of model instances.
        """
        with self.session_factory() as session:
            return session.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs: Any) -> ModelType:
        """
        Creates a new record in the database.

        Args:
            **kwargs: A dictionary of attributes for the new record.

        Returns:
            The newly created model instance.
        """
        with self.session_factory() as session:
            # Use session.begin() to ensure the transaction is atomic.
            # It automatically commits on success or rolls back on error.
            with session.begin():
                db_obj = self.model(**kwargs)
                session.add(db_obj)
            session.refresh(db_obj)
            return db_obj

    def update(self, pk: Any, **kwargs: Any) -> Optional[ModelType]:
        """
        Updates an existing record identified by its primary key.

        Args:
            pk: The primary key of the record to update.
            **kwargs: The new values for the attributes to update.

        Returns:
            The updated model instance, or None if the record was not found.
        """
        with self.session_factory() as session:
            with session.begin():
                db_obj = session.query(self.model).get(pk)
                if db_obj is None:
                    return None

                for key, value in kwargs.items():
                    if hasattr(db_obj, key):
                        setattr(db_obj, key, value)

                session.add(db_obj)
            session.refresh(db_obj)
            return db_obj

    def delete(self, pk: Any) -> bool:
        """
        Deletes a record by its primary key.

        Args:
            pk: The primary key of the record to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        with self.session_factory() as session:
            with session.begin():
                db_obj = session.query(self.model).get(pk)
                if db_obj is None:
                    return False
                session.delete(db_obj)
            return True
