from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.cache import invalidate_prefix
from app.auth import get_current_active_user
from app.tasks import prime_endpoints

router = APIRouter(prefix="/admin", tags=["Administration"])
class FlushRequest(BaseModel):
    prefix: str | None = None
    
@router.post("/cache/flush")
async def flush_cache(body: FlushRequest, user: dict = Depends(get_current_active_user)):
    prefix = body.prefix or ""
    deleted = await invalidate_prefix(prefix)
    if deleted == 0:
        # could mean no keys or redis not available
        return {"deleted_keys": 0}
    return {"deleted_keys": deleted}

@router.post("/cache/prime")
async def prime_cache(user: dict = Depends(get_current_active_user)):
    task = prime_endpoints.delay()
    return {"task_id": task.id, "status": "queued"}
