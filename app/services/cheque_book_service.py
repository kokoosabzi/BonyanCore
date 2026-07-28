from sqlalchemy.orm import Session
from app.models.cheque_book import ChequeBook, Cheque, ChequeStatus
from app.schemas.cheque_book import ChequeBookCreate, ChequeBookUpdate

class ChequeBookService:
    @staticmethod
    def create(db: Session, data: ChequeBookCreate) -> ChequeBook:
        cheque_book = ChequeBook(
            bank_account_id=data.bank_account_id,
            serial_no=data.serial_no,
            serial_number=data.serial_number,
            total_pages=data.total_pages,
            min_pages=data.min_pages,
            title=data.title,
            receive_date=data.receive_date,
            signatories=data.signatories,
            description=data.description
        )
        db.add(cheque_book)
        db.flush()

        for i in range(data.total_pages):
            cheque = Cheque(
                cheque_book_id=cheque_book.id,
                cheque_no=str(i + 1).zfill(3),
                status=ChequeStatus.AVAILABLE
            )
            db.add(cheque)

        db.commit()
        db.refresh(cheque_book)
        return cheque_book

    @staticmethod
    def get_by_id(db: Session, book_id: int) -> ChequeBook | None:
        return db.query(ChequeBook).filter(
            ChequeBook.id == book_id,
            ChequeBook.is_deleted == False
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(ChequeBook).filter(
            ChequeBook.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, book_id: int, data: ChequeBookUpdate) -> ChequeBook | None:
        book = ChequeBookService.get_by_id(db, book_id)
        if not book:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete(db: Session, book_id: int) -> bool:
        book = ChequeBookService.get_by_id(db, book_id)
        if not book:
            return False
        book.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_cheque(db: Session, cheque_id: int) -> Cheque | None:
        return db.query(Cheque).filter(
            Cheque.id == cheque_id,
            Cheque.is_deleted == False
        ).first()

    @staticmethod
    def use_cheque(db: Session, cheque_id: int, receipt_id: int) -> Cheque | None:
        cheque = ChequeBookService.get_cheque(db, cheque_id)
        if not cheque:
            return None
        if cheque.status != ChequeStatus.AVAILABLE:
            raise ValueError("این چک قبلاً استفاده شده است")
        cheque.status = ChequeStatus.USED
        cheque.receipt_id = receipt_id
        db.commit()
        db.refresh(cheque)
        return cheque