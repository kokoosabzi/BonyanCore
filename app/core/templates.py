from fastapi.templating import Jinja2Templates

from app.utils.jalali import to_jalali


def create_templates(directory: str = "app/templates") -> Jinja2Templates:
    """Create Jinja templates with app-wide filters."""
    templates = Jinja2Templates(directory=directory)
    templates.env.filters["jalali"] = to_jalali
    return templates
