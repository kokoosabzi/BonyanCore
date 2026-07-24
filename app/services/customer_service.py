from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    @staticmethod
    def create(db: Session, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Customer | None:
        return db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()

    @staticmethod
    def get_by_customer_no(db: Session, customer_no: str) -> Customer | None:
        return db.query(Customer).filter(Customer.customer_no == customer_no, Customer.is_deleted == False).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, search: str = None):
        query = db.query(Customer).filter(Customer.is_deleted == False)
        if search:
            query = query.filter(
                or_(
                    Customer.full_name.ilike(f"%{search}%"),
                    Customer.customer_no.ilike(f"%{search}%"),
                    Customer.national_code.ilike(f"%{search}%"),
                    Customer.mobile.ilike(f"%{search}%")
                )
            )
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, customer_id: int, data: CustomerUpdate) -> Customer | None:
        customer = CustomerService.get_by_id(db, customer_id)
        if not customer:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete(db: Session, customer_id: int) -> bool:
        customer = CustomerService.get_by_id(db, customer_id)
        if not customer:
            return False
        customer.is_deleted = True
        db.commit()
        return True