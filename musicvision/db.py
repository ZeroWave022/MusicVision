from datetime import datetime
from sqlalchemy import (
    String,
    BigInteger,
    SmallInteger,
    DateTime,
    ForeignKey,
    create_engine,
    select,
    update,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from musicvision.env import getenv

DB_URI = getenv("DB_URI")
db = create_engine(DB_URI)

DBSession = sessionmaker(db)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    last_logged_in: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow()
    )
    last_updated: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow())


class UserAuth(Base):
    __tablename__ = "userauth"

    id: Mapped[str] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    access_token: Mapped[str] = mapped_column(String)
    token_type: Mapped[str] = mapped_column(String)
    scope: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)
    expires_at: Mapped[int] = mapped_column(BigInteger)
