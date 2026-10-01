from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import Film
from ..db.schemas import FilmCreate, FilmUpdate


def create_film(session: Session, payload: FilmCreate) -> Film:
    film = Film(**payload.model_dump())
    session.add(film)
    session.commit()
    session.refresh(film)
    return film


def get_film(session: Session, film_id: int) -> Film | None:
    return session.get(Film, film_id)


def get_films(
    session: Session,
    limit: int = 20,
    offset: int = 0,
) -> list[Film]:
    stmt = select(Film)
    stmt = stmt.limit(limit).offset(offset)
    return list(session.scalars(stmt).all())


def update_film(session: Session, film: Film, payload: FilmUpdate) -> Film:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(film, field, value)
    session.commit()
    session.refresh(film)
    return film


def delete_film(session: Session, film: Film) -> None:
    session.delete(film)
    session.commit()
