from . import Base
from .base import bigint

from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = 'users'

    id: Mapped[bigint] = mapped_column(primary_key=True)

    join_date: Mapped[datetime] = mapped_column(default=datetime.now)
    block_date: Mapped[Optional[datetime]]

    ref: Mapped[Optional[str]]
    subbed: Mapped[bool] = mapped_column(default=False)
    subbed_before: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[int] = mapped_column(default=10)
    ref_balance: Mapped[int] = mapped_column(default=0)
    api_key: Mapped[UUID] = mapped_column(default=uuid4)

    chat_only: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
