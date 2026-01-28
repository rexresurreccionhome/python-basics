from typing import Self
from fraud_detection_system.models import (
    FraudRecord,
    PersonalInfo,
    DeviceInfo,
    PaymentMethodEnum,
    BankAccount,
    CreditCard
)


class FraudRecordBuilder:
    def __init__(self) -> None:
        self._amount = 100.0
        self._personal_info = PersonalInfo(
            name="John Doe",
            age=30,
            ssn="123-45-6789",
            email="jdoe@example.com",
            phone_number="555-1234",
        )
        self._device_info = DeviceInfo(ip_address="10.0.0.1")
        self._payment_method = PaymentMethodEnum.ACH
        self._bank_account = BankAccount(routing_number=111000025, account_number=123456789)
        self._credit_card = None

    def with_amount(self, amount: float) -> Self:
        self._amount = amount
        return self
    
    def with_personal_info(self, personal_info: PersonalInfo) -> Self:
        self._personal_info = personal_info
        return self
    
    def with_device_info(self, device_info: DeviceInfo) -> Self:
        self._device_info = device_info
        return self
    
    def with_payment_method(self, payment_method: PaymentMethodEnum) -> Self:
        self._payment_method = payment_method
        return self
    
    def with_bank_account(self, bank_account: BankAccount | None) -> Self:
        self._bank_account = bank_account
        return self
    
    def with_credit_card(self, credit_card: CreditCard | None) -> Self:
        self._credit_card = credit_card
        return self

    def build(self) -> FraudRecord:
        return FraudRecord(
            amount=self._amount,
            personal_info=self._personal_info,
            device_info=self._device_info,
            payment_method=self._payment_method,
            bank_account=self._bank_account,
            credit_card=self._credit_card
        )
