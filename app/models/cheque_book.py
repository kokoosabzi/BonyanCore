from sqlalchemy import Column, String, Integer, BigInteger, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class ChequeStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    USED = "USED"
    CANCELLED = "CANCELLED"

class ChequeBook(BaseModel):
    __tablename__ = "cheque_books"

    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=False)
    serial_no = Column(String(20), nullable=False)
    serial_number = Column(String(20), nullable=False)
    total_pages = Column(Integer, nullable=False)
    min_pages = Column(Integer, default=0)
    title = Column(String(200), nullable=True)
    receive_date = Column(Date, nullable=True)
    signatories = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE")

    # Relationships
    bank_account = relationship("BankAccount")
    cheques = relationship("Cheque", back_populates="cheque_book")

class Cheque(BaseModel):
    __tablename__ = "cheques"

    cheque_book_id = Column(BigInteger, ForeignKey("cheque_books.id"), nullable=False)
    cheque_no = Column(String(20), nullable=False)
    amount = Column(BigInteger, nullable=True)
    due_date = Column(Date, nullable=True)
    payee = Column(String(200), nullable=True)
    status = Column(Enum(ChequeStatus), default=ChequeStatus.AVAILABLE)
    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    cheque_book = relationship("ChequeBook", back_populates="cheques")
    receipt = relationship("Receipt")