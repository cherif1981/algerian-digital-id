from abc import ABC, abstractmethod
from typing import Optional
from .models import Identity


class IdentityStore(ABC):
    """واجهة مخزن الهوية — تسمح بالتبديل بين تنفيذات مختلفة."""

    @abstractmethod
    async def create(self, identity: Identity) -> Identity: ...

    @abstractmethod
    async def get_by_id(self, identity_id: str) -> Optional[Identity]: ...

    @abstractmethod
    async def get_by_nin(self, nin: str) -> Optional[Identity]: ...

    @abstractmethod
    async def update_status(
        self, identity_id: str, status: str, verification_level: str
    ) -> Identity: ...

    @abstractmethod
    async def delete(self, identity_id: str) -> None: ...