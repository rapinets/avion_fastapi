from pathlib import Path

from fastapi.templating import Jinja2Templates


# Шлях до папки app/api
WEB_DIR = Path(__file__).resolve().parent

# Підключення папки app/api/templates із HTML-шаблонами
templates = Jinja2Templates(
    directory=str(WEB_DIR / "templates")
)