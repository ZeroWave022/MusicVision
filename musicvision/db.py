from datetime import datetime
from sqlalchemy import (
    String,
    SmallInteger,
    Integer,
    BigInteger,
    DateTime,
    ForeignKey,
    create_engine,
    select,
    update,
)
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
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

    auth: Mapped["UserAuth"] = relationship(
        back_populates="user", cascade="all, delete"
    )
    tracks: Mapped[list["Track"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    artists: Mapped[list["Artist"]] = relationship(
        back_populates="user", cascade="all, delete"
    )


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

    user: Mapped["User"] = relationship(back_populates="auth")


class Track(Base):
    __tablename__ = "track"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    track_id: Mapped[str] = mapped_column(String)
    time_frame: Mapped[str] = mapped_column(String)
    popularity: Mapped[int] = mapped_column(SmallInteger)
    added_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow())

    user: Mapped["User"] = relationship(back_populates="tracks")


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    artist_id: Mapped[str] = mapped_column(String)
    time_frame: Mapped[str] = mapped_column(String)
    popularity: Mapped[int] = mapped_column(SmallInteger)
    added_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow())

    user: Mapped["User"] = relationship(back_populates="artists")
