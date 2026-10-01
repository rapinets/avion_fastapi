from sqlalchemy import JSON, String, INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Film(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(INTEGER)
    genre: Mapped[str] = mapped_column(String(100))
    producer: Mapped[str] = mapped_column(String(100))
    duration: Mapped[int] = mapped_column(INTEGER)
    actors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list,)

