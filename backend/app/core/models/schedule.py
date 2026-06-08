from sqlalchemy import (
    Integer,
    UniqueConstraint,
    UUID,
    ForeignKey,
    CheckConstraint,
    Date,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from .helpers import Base
from .mixins import UUIDPKMixin, TimestampMixin
from ...enums import ActivityType


class SchedulePlan(Base, UUIDPKMixin):
    speciality_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "specialities.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "subjects.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    semester_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "semesters.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    lecture_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    practice_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("year BETWEEN 1 AND 7", name="ck_schedule_plan_year_range"),
        CheckConstraint(
            "lecture_hours > 0 AND lecture_hours <= 2000",
            name="ck_lecture_hours_range",
        ),
        CheckConstraint(
            "practice_hours > 0 AND practice_hours <= 1000",
            name="ck_practice_hours_range",
        ),
        CheckConstraint(
            "lecture_hours > 0 OR practice_hours > 0",
            name="ck_at_least_one_hour_type",
        ),
        UniqueConstraint(
            "speciality_id",
            "subject_id",
            "semester_id",
            name="uq_schedule_plan_speciality_subject_semester",
        ),
    )

    # TODO: rel


class ScheduleItem(Base, UUIDPKMixin, TimestampMixin):
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    semester_id: Mapped[UUID] = mapped_column(
        ForeignKey("semesters.id", ondelete="RESTRICT"),
        nullable=False,
    )
    time_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("time_slots.id", ondelete="RESTRICT"),
        nullable=False,
    )

    class_date: Mapped[Date] = mapped_column(Date, nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(
        ENUM(ActivityType, name="activity_type", create_type=True),
        default=ActivityType.lecture,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "group_id", "class_date", "time_slot_id", name="uq_schedule_group_date_time"
        ),
        UniqueConstraint(
            "teacher_id",
            "class_date",
            "time_slot_id",
            name="uq_schedule_teacher_date_time",
        ),
        UniqueConstraint(
            "room_id", "class_date", "time_slot_id", name="uq_schedule_room_date_time"
        ),
    )
    # TODO: rel
