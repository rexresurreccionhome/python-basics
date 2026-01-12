from abc import ABC, abstractmethod
from random import choice

from payment_system_with_retry.exceptions import DummyGatewayError
from payment_system_with_retry.models import (
    Payment,
    PaymentTransaction,
)
from payment_system_with_retry.payment_retry import attempt_payment_decorator


MAX_ATTEMPTS = 3


class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, payment: Payment) -> PaymentTransaction:
        """
        Simulates a payment processor with random success or failure.
        Returns a PaymentTransaction on success.
        
        :param payment: Payment object containing payment details
        :return: PaymentTransaction object representing the result of the payment processing
        :rtype: PaymentTransaction
        """
        pass


class BankOfIllinoisPaymentProcessor(PaymentProcessor):
    @attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=MAX_ATTEMPTS)
    def process_payment(self, payment: Payment) -> PaymentTransaction:
        is_success = choice([True, False]) # simulate a success or failure
        if is_success:
            return PaymentTransaction(
                amount=payment.amount,
                transaction_id="IL-12345" # return a transaction ID
            )
        # simulate a payment gateway error
        raise DummyGatewayError("IL-001: Service Unavailable.")


class BankOfVirginiaPaymentProcessor(PaymentProcessor):
    @attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=MAX_ATTEMPTS)
    def process_payment(self, payment: Payment) -> PaymentTransaction:
        is_success = choice([True, False]) # simulate a success or failure
        if is_success:
            return PaymentTransaction(
                amount=payment.amount,
                transaction_id="VA-12345" # return a transaction ID
            )
        # simulate a payment gateway error
        raise DummyGatewayError("VA-001: Service Unavailable.")


class PaymentProcessorFactory:
    _payment_processors: dict[str, type[PaymentProcessor]] = {}

    @classmethod
    def register_payment_processor(cls, state_code: str, processor: type[PaymentProcessor]) -> None:
        cls._payment_processors[state_code] = processor

    @classmethod
    def get_payment_processor(cls, state_code: str) -> PaymentProcessor:
        if state_code in cls._payment_processors:
            return cls._payment_processors[state_code]()
        
        raise ValueError(f"Unsupported bank: {state_code}")


def register_state_payment_processors() -> None:
    PaymentProcessorFactory.register_payment_processor("IL", BankOfIllinoisPaymentProcessor)
    PaymentProcessorFactory.register_payment_processor("VA", BankOfVirginiaPaymentProcessor)
