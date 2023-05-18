from . import Base
from .base import bigint
from .dialogue import Dialogue

from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'users'

    id: Mapped[bigint] = mapped_column(primary_key=True, autoincrement=True)

    join_date: Mapped[datetime] = mapped_column(default=datetime.now)
    block_date: Mapped[Optional[datetime]]

    ref: Mapped[Optional[str]]
    subbed: Mapped[bool] = mapped_column(default=False)
    subbed_before: Mapped[bool] = mapped_column(default=False)

    invited: Mapped[int] = mapped_column(default=0)
    age: Mapped[Optional[int]]
    is_man: Mapped[Optional[bool]]

    vip_time: Mapped[datetime] = mapped_column(default=datetime.fromtimestamp(0))
    chat_only: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    partner: Mapped[Optional["Dialogue"]] = relationship(
        primaryjoin="or_("
        "    User.id==Dialogue.first," 
        "    User.id==Dialogue.second,"
        ")",
    )

    @property
    def partner_id(self) -> int:

        return self.partner.get_id(self.id)    

    @property
    def is_vip(self) -> bool:

        return (
            self.vip_time is not None
             and self.vip_time > datetime.now()
        )

    def add_vip(self, days: int):
        """
        Add VIP days to user. You need to commit after.

        :param int days: Amount of days
        """

        self.vip_time = max(self.vip_time, datetime.now()) + timedelta(days=days)
