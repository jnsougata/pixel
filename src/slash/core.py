from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class BaseInteraction:
    id: int
    version: int
    token: str
    type: int
    data: dict
    application_id: int
    guild_id: Optional[Union[int, str]] = None
    channel_id: Optional[Union[int, str]] = None
    message: Optional[dict] = None
    member: Optional[dict] = None
    user: Optional[dict] = None
    locale: Optional[str] = None
    guild_locale: Optional[str] = None


@dataclass(frozen=True)
class BaseInteractionData:
    id: Union[int, str]
    name: str
    type: int
    resolved: Optional[dict] = None
    custom_id: Optional[str] = None
    options: Optional[dict] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    target_id: Optional[str] = None


@dataclass(frozen=True)
class BaseSlashOption:
    name: str
    type: int
    value: Union[str, int, float, bool]
    options: Optional[list] = None
    focused: Optional[bool] = None
