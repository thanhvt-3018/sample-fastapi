from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.workspace import Workspace, WorkspaceMember
    from app.models.task import Task
    from app.models.comment import Comment


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", native_enum=False), default=UserRole.MEMBER, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)

    owned_workspaces: Mapped[list[Workspace]] = relationship(
        back_populates="owner", lazy="raise")
    workspace_memberships: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="user", lazy="raise")
    assigned_tasks: Mapped[list[Task]] = relationship(
        foreign_keys="Task.assignee_id", back_populates="assignee", lazy="raise")
    created_tasks: Mapped[list[Task]] = relationship(
        foreign_keys="Task.created_by", back_populates="creator", lazy="raise")
    comments: Mapped[list[Comment]] = relationship(
        back_populates="author", lazy="raise")
