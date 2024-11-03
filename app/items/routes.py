from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from . import schemas, items_logic
from ..auth.models import User

router = APIRouter()


@router.post("/items/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return items_logic.create_item(db=db, item=item, user_id=current_user.id)


@router.get("/items/", response_model=list[schemas.ItemResponse])
async def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    query: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400, detail="min_price cannot be greater than max_price"
        )

    return items_logic.get_items(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        query=query,
    )


@router.get("/items/{item_id}", response_model=schemas.ItemResponse)
async def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = items_logic.get_item(db=db, item_id=item_id, user_id=current_user.id)
    return item


@router.put("/items/{item_id}", response_model=schemas.ItemResponse)
async def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return items_logic.update_item(
        db=db, item_id=item_id, item=item, user_id=current_user.id
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items_logic.delete_item(db=db, item_id=item_id, user_id=current_user.id)
    return {"message": "Item deleted successfully"}
