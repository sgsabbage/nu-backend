from typing import Protocol, runtime_checkable

from .models import CharacterHealth


@runtime_checkable
class HasHealth(Protocol):
    health: CharacterHealth
