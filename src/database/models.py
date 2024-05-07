from sqlalchemy import Integer, String, func, Date, DateTime, Boolean

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'User(name={self.name}, email={self.email})'


class Contact(Base):
    __tablename__ = 'contacts'
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Date] = mapped_column(Date)
    user_id: Mapped[User] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE')
    )
    # Alchemy
    user: Mapped["Contact"] = relationship("User", backref="contacts", lazy="selectin")

    def __repr__(self):
        return f'Contact(name={self.name}, surname={self.surname}, email={self.email}, phone={self.phone})'
