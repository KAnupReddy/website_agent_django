import json
import re
import shutil
from pathlib import Path

from django.conf import settings


def slugify(name: str) -> str:
    """Same rule as the PHP app: lowercase, non-alphanumerics → '-', trimmed."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def build_dir_for(name: str) -> Path:
    return Path(settings.BUILD_DIR) / slugify(name)


def remove_build_dir(name: str) -> None:
    shutil.rmtree(build_dir_for(name), ignore_errors=True)


def parse_json_response(raw: str):
    """Parse a model reply as a JSON object, tolerating ```json fences."""
    text = re.sub(r'^```(?:json)?\s*', '', (raw or '').strip(), flags=re.I)
    text = re.sub(r'\s*```$', '', text)
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def text(value) -> str:
    """Render a model value as plain text (lists are space-joined, None is '')."""
    if isinstance(value, list):
        return ' '.join(str(v) for v in value)
    return '' if value is None else str(value)
