from typing import Any, Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from ...db import schemas
from ...dependencies import SessionDep
from ...services import film_service

from app.api.templating import templates

router = APIRouter(prefix="/films", tags=["films"])

def validation_messages(error: ValidationError) -> list[str]:
    """Create readable messages for validation errors shown in an HTML form."""
    return [
        f"{item['loc'][-1]}: {item['msg']}"
        for item in error.errors()
    ]

def film_form_response(
    *,
    request: Request,
    title: str,
    action_url: str,
    submit_label: str,
    values: dict[str, Any],
    errors: list[str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="films/form.html",
        context={
            "page_title": title,
            "action_url": action_url,
            "submit_label": submit_label,
            "values": values,
            "errors": errors or [],
        },
        status_code=status_code,
    )


@router.post(
    "/",
    response_model=schemas.FilmResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_film",
)
def create_film(request: Request, payload: Annotated[schemas.FilmCreate, Form()], db: SessionDep) -> RedirectResponse:
    try:
        film_service.create_film(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create film",
        )
    return RedirectResponse(
        url=request.url_for("films"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/", response_model=list[schemas.FilmResponse], name="films")
def read_films(
    request: Request,
    db: SessionDep,
    limit: int = 20,
    offset: int = 0,
):
    films = film_service.get_films(db, limit, offset)
    return templates.TemplateResponse(request=request, name="films/list.html", context={"page_title": "Усі фільми", "films": films})

@router.get("/create", response_class=HTMLResponse, name="create_film_form")
def create_film_form(request: Request) -> HTMLResponse:
    return film_form_response(request=request, title="Додати фільм", action_url=str(request.url_for("create_film")), submit_label="Додати фільм",
                              values={"title": "", "producer": "", "genre": "", "year": "", "duration": "", "actors": ""})


@router.get("/{film_id}", response_model=schemas.FilmResponse, name="film_detail")
def read_film(film_id: int, db: SessionDep, request: Request):
    film = film_service.get_film(db, film_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film not found",
        )
    return templates.TemplateResponse(request=request, name="films/detail.html", context={"page_title": "Фільм","film": film})


@router.get("/{film_id}/edit/", response_class=HTMLResponse, name="edit_film_form")
def edit_film_form(film_id: int, db: SessionDep, request: Request) -> HTMLResponse:
    film = film_service.get_film(db, film_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фільм не знайдено",
        )
    values = {
        "title": film.title,
        "producer": film.producer,
        "genre": film.genre,
        "year": film.year,
        "duration": film.duration,
        "actors": ", ".join(film.actors or []),
    }
    return film_form_response(
        request=request,
        title="Редагувати фільм",
        action_url=str(
            request.url_for(
                "update_film",
                film_id=film.id,
            )
        ),
        submit_label="Зберегти зміни",
        values=values,
    )


@router.post("/{film_id}/edit", response_model=schemas.FilmResponse, name="update_film")
def update_film(film_id: int, request: Request, payload: Annotated[schemas.FilmUpdate, Form()], db: SessionDep) -> RedirectResponse:
    film = film_service.get_film(db, film_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film not found",
        )
    try:
        film = film_service.update_film(db, film, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update film",
        )
    return RedirectResponse(
        url=request.url_for("films"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{film_id}/delete", status_code=status.HTTP_204_NO_CONTENT, name="delete_film")
def delete_film(film_id: int, db: SessionDep, request: Request) -> RedirectResponse:
    film = film_service.get_film(db, film_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film not found",
        )
    film_service.delete_film(db, film)
    return RedirectResponse(
        url=request.url_for("films"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
