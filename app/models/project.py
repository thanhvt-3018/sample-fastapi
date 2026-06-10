from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ProjectStatus
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.task import Task
    from app.models.label import Label


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey(
        "workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus, name="project_status", native_enum=False), default=ProjectStatus.ACTIVE, nullable=False)

    workspace: Mapped[Workspace] = relationship(
        back_populates="projects", lazy="raise")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="project", lazy="raise", cascade="all, delete-orphan")
    labels: Mapped[list[Label]] = relationship(
        back_populates="project", lazy="raise", cascade="all, delete-orphan")
