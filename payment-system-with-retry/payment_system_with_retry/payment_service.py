from payment_system_with_retry.models import Payment
from payment_system_with_retry.payment_retry import AttemptPaymentError
from payment_system_with_retry.payment_processors import PaymentProcessor


class PaymentProcessService:
    _payment_processor: PaymentProcessor

    def __init__(self, payment_processor: PaymentProcessor) -> None:
        self._payment_processor = payment_processor

    def process_payment(self, payment: Payment) -> Payment:
        try:
            payment.transaction = self._payment_processor.process_payment(payment)
        except AttemptPaymentError as error:
            # Handle the error as needed, e.g., log it or re-raise
            payment.attempt_count += error.count
            payment.errors.extend(error.errors)
        return payment
