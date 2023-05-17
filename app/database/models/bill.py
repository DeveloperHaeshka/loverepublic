from . import Base
from .base import bigint

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class Bill(Base):
    __tablename__ = 'bills'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[bigint]
    amount: Mapped[int] 
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
