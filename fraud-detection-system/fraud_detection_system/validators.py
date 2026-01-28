import re
from abc import ABC, abstractmethod

from fraud_detection_system.models import FraudRecord


class ValidationError(Exception):
    pass


class DataValidation(ABC):
    @abstractmethod
    def validate(self, fraud_record: FraudRecord) -> list[ValidationError]:
        pass


class PersonalInfoDataValidation(DataValidation):
    def validate(self, fraud_record: FraudRecord) -> list[ValidationError]:
        errors = []
        errors.extend(self.name_validation(fraud_record.personal_info.name))
        errors.extend(self.age_validation(fraud_record.personal_info.age))
        errors.extend(self.ssn_validation(fraud_record.personal_info.ssn))
        errors.extend(self.phone_validation(fraud_record.personal_info.phone_number))
        errors.extend(self.email_validation(fraud_record.personal_info.email))
        return errors
    
    def name_validation(self, name: str) -> list[ValidationError]:
        errors = []
        if not name:
            errors.append(ValidationError("Name is missing"))
        return errors
    
    def age_validation(self, age: int) -> list[ValidationError]:
        errors = []
        if not age or age < 0:
            errors.append(ValidationError("Invalid age"))
        if age < 18:
            errors.append(ValidationError("Age must be at least 18"))
        return errors

    def email_validation(self, email: str) -> list[ValidationError]:
        errors = []
        if not email:
            errors.append(ValidationError("Email is missing"))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append(ValidationError("Invalid email format"))
        return errors

    def phone_validation(self, phone_number: str) -> list[ValidationError]:
        errors = []
        if not phone_number:
            errors.append(ValidationError("Phone number is missing"))
        if not re.match(r"^\+?1?\d{9,15}$", phone_number): # Example Good Format: +12345678900
            errors.append(ValidationError("Invalid phone number format"))
        return errors

    def ssn_validation(self, ssn: str) -> list[ValidationError]:
        errors = []
        if not ssn:
            errors.append(ValidationError("SSN is missing"))
        if not re.match(r"^\d{3}-\d{2}-\d{4}$", ssn): # Example Good Format: 123-45-6789
            errors.append(ValidationError("Invalid SSN format"))
        return errors


class ACHDataValidation(DataValidation):
    def validate(self, fraud_record: FraudRecord) -> list[ValidationError]:
        errors = []
        errors.extend(self.account_number_validation(fraud_record.bank_account.account_number))
        errors.extend(self.routing_number_validation(fraud_record.bank_account.routing_number))
        return errors

    def account_number_validation(self, account_number: str) -> list[ValidationError]:
        errors = []
        if not account_number:
            errors.append(ValidationError("Account number is missing"))
        return errors

    def routing_number_validation(self, routing_number: str) -> list[ValidationError]:
        errors = []
        if not routing_number:
            errors.append(ValidationError("Routing number is missing"))
        return errors


class CreditCardDataValidation(DataValidation):
    def validate(self, fraud_record: FraudRecord) -> list[ValidationError]:
        errors = []
        errors.extend(self.card_number_validation(fraud_record.credit_card.card_number))
        errors.extend(self.expiry_date_validation(fraud_record.credit_card.expiry_date))
        errors.extend(self.cvv_validation(fraud_record.credit_card.cvv))
        errors.extend(self.zip_code_validation(fraud_record.credit_card.zip_code))
        return errors
    
    def card_number_validation(self, card_number: str) -> list[ValidationError]:
        errors = []
        if not card_number:
            errors.append(ValidationError("Card number is missing"))
        return errors

    def expiry_date_validation(self, expiry_date: str) -> list[ValidationError]:
        errors = []
        if not expiry_date:
            errors.append(ValidationError("Expiry date is missing"))
        return errors

    def cvv_validation(self, cvv: int) -> list[ValidationError]:
        errors = []
        if not cvv:
            errors.append(ValidationError("CVV is missing"))
        if len(str(cvv)) != 3:
            errors.append(ValidationError("CVV must be 3 digits"))
        return errors
    
    def zip_code_validation(self, zip_code: str) -> list[ValidationError]:
        errors = []
        if not zip_code:
            errors.append(ValidationError("Zip code is missing"))
        return errors


class DataValidator(ABC):
    @abstractmethod
    def create_validator(self) -> DataValidation:
        pass

    def validate(self, fraud_record: FraudRecord) -> list[ValidationError]:
        validator = self.create_validator()
        return validator.validate(fraud_record)


class PersonalInfoDataValidator(DataValidator):
    def create_validator(self) -> DataValidation:
        return PersonalInfoDataValidation()


class ACHDataValidator(DataValidator):
    def create_validator(self) -> DataValidation:
        return ACHDataValidation()


class CreditCardDataValidator(DataValidator):
    def create_validator(self) -> DataValidation:
        return CreditCardDataValidation()


class DataValidatorBuilder:
    _validator: DataValidator

    def __init__(self) -> None:
        self._validator = []
    
    def with_personal_info_validator(self) -> None:
        self._validator.append(PersonalInfoDataValidator())

    def with_ach_data_validator(self) -> None:
        self._validator.append(ACHDataValidator())
    
    def with_credit_card_data_validator(self) -> None:
        self._validator.append(CreditCardDataValidator())
    
    def build_data_validators(self) -> list[DataValidator]:
        return self._validator
