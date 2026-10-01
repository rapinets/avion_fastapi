from pydantic import BaseModel, ConfigDict, Field

class FilmBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    year: int = Field(gt=1900, lt=2027)
    genre: str = Field(min_length=1, max_length=200)
    producer: str = Field(min_length=1, max_length=200)
    duration: int = Field(gt=0)
    actors: list[str] = Field(min_length=1, max_length=50)


class FilmCreate(FilmBase):
    pass


class FilmUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    genre: str | None = None
    producer: str | None = None
    duration: int | None = None
    actors: list[str] | None = None

class FilmResponse(FilmBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
