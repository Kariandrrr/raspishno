from sqlalchemy import (
    String,
    Integer, UniqueConstraint, UUID, ForeignKey, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .helpers import Base
from .mixins import UUIDPKMixin
from ...enums import RoomType


class Building(Base, UUIDPKMixin):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)

    #rel
    rooms: Mapped[list["Room"]] = relationship(back_populates="building", cascade="all,delete-orphan")


class Room(Base, UUIDPKMixin):
    room_number: Mapped[str] = mapped_column(String(10), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[RoomType] = mapped_column(ENUM(RoomType, name="room_type", create_type=True),
                                                default=RoomType.common_class)
    building_id: Mapped[UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)

    #rel
    building: Mapped["Building"] = relationship(back_populates="rooms")

    __table_args__ =(
        UniqueConstraint(
            'building_id',
        'room_number',
        name='unique_room_per_building'
        ),
        CheckConstraint('capacity > 0', name='capacity_check'),
    )


