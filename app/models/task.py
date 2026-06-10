from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TaskPriority, TaskStatus
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.label import Label
    from app.models.comment import Comment


task_labels = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", ForeignKey(
        "tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", ForeignKey("labels.id",
           ondelete="CASCADE"), primary_key=True),
)


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey(
        "projects.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey(
        "users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="task_status", native_enum=False), default=TaskStatus.TODO, nullable=False, index=True)
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, name="task_priority", native_enum=False), default=TaskPriority.MEDIUM, nullable=False, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    project: Mapped[Project] = relationship(
        back_populates="tasks", lazy="raise")
    assignee: Mapped[User | None] = relationship(
        foreign_keys=[assignee_id], back_populates="assigned_tasks", lazy="raise")
    creator: Mapped[User] = relationship(
        foreign_keys=[created_by], back_populates="created_tasks", lazy="raise")
    labels: Mapped[list[Label]] = relationship(
        secondary=task_labels, back_populates="tasks", lazy="raise")
    comments: Mapped[list[Comment]] = relationship(
        back_populates="task", lazy="raise", cascade="all, delete-orphan")
