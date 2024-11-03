from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import models, schemas


def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(db: Session, item_id: int, user_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.user_id == user_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate, user_id: int):
    db_item = get_item(db, item_id, user_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this item"
        )
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int, user_id: int):
    db_item = get_item(db, item_id, user_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )
    db.delete(db_item)
    db.commit()
    return db_item


def get_items(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    min_price: float = None,
    max_price: float = None,
    query: str = None,
):
    base_query = db.query(models.Item).filter(models.Item.user_id == user_id)

    if min_price is not None:
        base_query = base_query.filter(models.Item.price >= min_price)
    if max_price is not None:
        base_query = base_query.filter(models.Item.price <= max_price)

    if query:
        search = f"%{query}%"
        base_query = base_query.filter(
            or_(models.Item.name.ilike(search), models.Item.description.ilike(search))
        )

    return base_query.offset(skip).limit(limit).all()
