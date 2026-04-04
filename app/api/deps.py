from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

DbSession: TypeAlias = Annotated[Session, Depends(get_db)]
