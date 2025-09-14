from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.database.db import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(
        contact: ContactCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        additional_data=contact.additional_data,
        user_id=current_user.id
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


@router.get("/", response_model=List[ContactResponse])
def get_contacts(
        skip: int = 0,
        limit: int = 100,
        first_name: Optional[str] = Query(None, description="Фільтр за ім'ям"),
        last_name: Optional[str] = Query(None, description="Фільтр за прізвищем"),
        email: Optional[str] = Query(None, description="Фільтр за електронною адресою"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contacts = query.offset(skip).limit(limit).all()

    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
def get_upcoming_birthdays(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    today = date.today()

    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()

    upcoming_birthdays = []
    for contact in contacts:
        birthday_month_day = (contact.birthday.month, contact.birthday.day)

        for i in range(8):  # від 0 до 7 включно
            check_date = today + timedelta(days=i)
            if (check_date.month, check_date.day) == birthday_month_day:
                upcoming_birthdays.append(contact)
                break

    return upcoming_birthdays


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")

    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
        contact_id: int,
        contact: ContactUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")

    update_data = contact.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)

    return db_contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")

    db.delete(db_contact)
    db.commit()

    return None
