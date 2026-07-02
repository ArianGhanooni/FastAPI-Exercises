import gettext
from pathlib import Path
from fastapi import Request

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALES_DIR = BASE_DIR / "locales"

SUPPORTED_LANGUAGES = ["en", "fa"]
DEFAULT_LANGUAGE = "en"


def get_translations(lang: str) -> gettext.GNUTranslations:
    mo_path = LOCALES_DIR / lang / "LC_MESSAGES" / "messages.mo"

    if mo_path.exists():
        with open(mo_path, "rb") as f:
            return gettext.GNUTranslations(f)

    return gettext.NullTranslations()


def detect_language(request: Request) -> str:
    lang = request.query_params.get("lang")

    if lang and lang in SUPPORTED_LANGUAGES:
        return lang

    accept_language = request.headers.get("Accept-Language", "")

    for supported in SUPPORTED_LANGUAGES:
        if supported in accept_language:
            return supported

    return DEFAULT_LANGUAGE
