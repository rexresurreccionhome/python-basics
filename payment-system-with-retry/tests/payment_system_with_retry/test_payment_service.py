from payment_system_with_retry.exceptions import AttemptPaymentError
from payment_system_with_retry.models import Payment, PaymentTransaction
from payment_system_with_retry.payment_service import PaymentProcessService


class TestPaymentProcessService:
    def test_process_payment__successful_payment_processing__returns_processed_payment(self, mocker):
        transaction = PaymentTransaction(amount=100, transaction_id="txn-123")
        payment_processor_mock = mocker.MagicMock()
        payment_processor_mock.process_payment.return_value = transaction
        service = PaymentProcessService(payment_processor_mock)
        processed_payment = service.process_payment(mocker.Mock())
        assert processed_payment.transaction == transaction
    
    def test_process_payment__payment_processing_fails_with_attempt_payment_error__update_payment_with_attempt_count_and_errors(self, mocker):
        payment = Payment(amount=150)
        payment_processor_mock = mocker.MagicMock()
        payment_processor_mock.process_payment.side_effect = AttemptPaymentError(count=2, errors=["Error 1", "Error 2"])
        service = PaymentProcessService(payment_processor_mock)
        processed_payment = service.process_payment(payment)
        assert processed_payment is payment
        assert processed_payment.attempt_count == 2
        assert processed_payment.errors == ["Error 1", "Error 2"]
