from pydantic import BaseModel, conint
from typing import Tuple
class PaginationParams(BaseModel):
    limit: conint(ge=1, le=100) = 50
    offset: conint(ge=0) = 0

def apply_pagination(df, limit: int, offset: int):
    if hasattr(df, 'iloc'):
        return df.iloc[offset: offset + limit]
    return df[offset: offset + limit]
