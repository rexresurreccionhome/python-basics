from dataclasses import dataclass, field
from uuid import uuid4
from enum import StrEnum


@dataclass
class PersonalInfo:
    name: str
    age: int
    ssn: str
    email: str | None = None
    phone_number: str | None = None


@dataclass
class DeviceInfo:
    ip_address: str


@dataclass
class BankAccount:
    routing_number: int
    account_number: int


@dataclass
class CreditCard:
    card_number: int
    expiry_date: str
    cvv: int
    zip_code: str


class PaymentMethodEnum(StrEnum):
    CREDIT_CARD = "CC"
    ACH = "ACH"


@dataclass
class FraudRecord:
    amount: float
    personal_info: PersonalInfo
    device_info: DeviceInfo
    payment_method: PaymentMethodEnum
    bank_account: BankAccount | None = None
    credit_card: CreditCard | None = None


class AccountStatusEnum(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    DECLINED = "declined"
    # CLOSED = "closed"
    REAPPLIED = "reapplied"


@dataclass
class Account:
    fraud_record: FraudRecord
    status: AccountStatusEnum = AccountStatusEnum.PENDING
    fraud_score: float = 0.00
    data_validation_errors: list[str] = field(default_factory=list)
    account_id: str = field(default_factory=lambda: str(uuid4()))
