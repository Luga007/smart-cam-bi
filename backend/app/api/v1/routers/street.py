from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.street import Street

router = APIRouter(prefix="/streets", tags=["Streets"])


@router.post("/")
def create_street(
    name: str,
    city_id: int,
    db: Session = Depends(get_db)
):

    street = Street(
        name=name,
        city_id=city_id
    )

    db.add(street)
    db.commit()
    db.refresh(street)

    return {
        "message": "Street created successfully",
        "street": street
    }

@router.get("/")
def get_streets(db: Session = Depends(get_db)):
    return db.query(Street).all()



@router.get("/{street_id}")
def get_street(street_id: int, db: Session = Depends(get_db)):

    street = db.query(Street).filter(
        Street.street_id == street_id
    ).first()

    if not street:
        raise HTTPException(status_code=404, detail="Street not found")

    return street



@router.delete("/{street_id}")
def delete_street(street_id: int, db: Session = Depends(get_db)):

    street = db.query(Street).filter(
        Street.street_id == street_id
    ).first()

    if not street:
        raise HTTPException(status_code=404, detail="Street not found")

    db.delete(street)
    db.commit()

    return {"message": "Street deleted"}