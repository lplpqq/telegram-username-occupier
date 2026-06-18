from dataclasses import dataclass
from typing import Optional

from fragment.models.status import Status


@dataclass
class Username:
    title: str
    exists: bool
    status: Optional[Status] = None
