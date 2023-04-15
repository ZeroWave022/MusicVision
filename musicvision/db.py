from sqlalchemy import String, BigInteger, create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from musicvision.env import getenv
from urllib.parse import urlparse

DB_URI = getenv("DB_URI")
db = create_engine(DB_URI)

DBSession = sessionmaker(db)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    access_token: Mapped[str] = mapped_column(String)
    token_type: Mapped[str] = mapped_column(String)
    scope: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)
    expires_at: Mapped[int] = mapped_column(BigInteger)
