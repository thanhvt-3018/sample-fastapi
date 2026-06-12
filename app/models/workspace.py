from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import WorkspaceMemberRole
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="RESTRICT"), nullable=False, index=True)

    owner: Mapped[User] = relationship(
        back_populates="owned_workspaces", lazy="raise")
    members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="workspace", lazy="raise", cascade="all, delete-orphan")
    projects: Mapped[list[Project]] = relationship(
        back_populates="workspace", lazy="raise", cascade="all, delete-orphan")


class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[int] = mapped_column(ForeignKey(
        "workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[WorkspaceMemberRole] = mapped_column(
        SAEnum(WorkspaceMemberRole, name="workspace_member_role", native_enum=False), nullable=False)

    workspace: Mapped[Workspace] = relationship(
        back_populates="members", lazy="raise")
    user: Mapped[User] = relationship(
        back_populates="workspace_memberships", lazy="raise")
