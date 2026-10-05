from fastapi import Request

from editalmind_ai.infrastructure.settings import Settings


def get_app_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings
