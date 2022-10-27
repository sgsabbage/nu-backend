from typing import Protocol, runtime_checkable

from .models import CharacterMagic


@runtime_checkable
class HasMagic(Protocol):
    magic: CharacterMagic
