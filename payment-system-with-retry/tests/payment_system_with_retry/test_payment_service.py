from payment_system_with_retry.exceptions import AttemptPaymentError
from payment_system_with_retry.models import Payment, PaymentTransaction
from payment_system_with_retry.payment_service import PaymentProcessService


class TestPaymentProcessService:
    def test_process_payment__successful_payment_processing__returns_processed_payment(self, mocker):
        transaction = PaymentTransaction(amount=100, transaction_id="txn-123")
        payment_processor_mock = mocker.MagicMock()
        payment_processor_mock.process_payment.return_value = transaction
        payment_processor_factory_mock = mocker.MagicMock()
        payment_processor_factory_mock.get_payment_processor.return_value = payment_processor_mock
        mocker.patch("payment_system_with_retry.payment_service.PaymentProcessorFactory", new=payment_processor_factory_mock)
        service = PaymentProcessService("IL")
        processed_payment = service.process_payment(mocker.Mock())
        assert processed_payment.transaction == transaction
        payment_processor_factory_mock.get_payment_processor.assert_called_once_with("IL")
    
    def test_process_payment__payment_processing_fails_with_attempt_payment_error__update_payment_with_attempt_count_and_errors(self, mocker):
        payment = Payment(amount=150)
        payment_processor_mock = mocker.MagicMock()
        payment_processor_mock.process_payment.side_effect = AttemptPaymentError(count=2, errors=["Error 1", "Error 2"])
        payment_processor_factory_mock = mocker.MagicMock()
        payment_processor_factory_mock.get_payment_processor.return_value = payment_processor_mock
        mocker.patch("payment_system_with_retry.payment_service.PaymentProcessorFactory", new=payment_processor_factory_mock)
        service = PaymentProcessService("XX")
        processed_payment = service.process_payment(payment)
        assert processed_payment is payment
        assert processed_payment.attempt_count == 2
        assert processed_payment.errors == ["Error 1", "Error 2"]
