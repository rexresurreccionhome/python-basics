import pytest

from payment_system_with_retry.exceptions import DummyGatewayError, AttemptPaymentError
from payment_system_with_retry.models import PaymentTransaction
from payment_system_with_retry.payment_retry import attempt_payment_decorator


def test_attempt_payment_decorator__invalid_max_attempts__raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=0)
    assert str(exc_info.value) == "max_attempts must be greater than 0"


def test_attempt_payment_decorator__valid_max_attempts__returns_decorator():
    decorator = attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=1)
    assert callable(decorator)


def test_attempt_payment_decorator__success_processing_payment__returns_transaction(mocker):
    class DummyProcessor:
        @attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=1)
        def process_payment(self, _):
            return PaymentTransaction(amount=100, transaction_id="txn-123")

    processor = DummyProcessor()
    transaction = processor.process_payment(mocker.Mock())
    assert isinstance(transaction, PaymentTransaction)
    assert transaction.amount == 100
    assert transaction.transaction_id == "txn-123"


def test_attempt_payment_decorator__transient_errors_then_success__returns_transaction(mocker):
    class DummyProcessor:
        def __init__(self):
            self.attempts = 0

        @attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=3)
        def process_payment(self, _):
            self.attempts += 1
            if self.attempts < 3:
                raise DummyGatewayError("Transient error")
            return PaymentTransaction(amount=200, transaction_id="txn-456")

    processor = DummyProcessor()
    transaction = processor.process_payment(mocker.Mock())
    assert isinstance(transaction, PaymentTransaction)
    assert transaction.amount == 200
    assert transaction.transaction_id == "txn-456"
    assert processor.attempts == 3


def test_attempt_payment_decorator__exceeds_max_attempts__raises_attempt_payment_error(mocker):
    class DummyProcessor:
        @attempt_payment_decorator(retry_exceptions=(DummyGatewayError,), max_attempts=2)
        def process_payment(self, _):
            raise DummyGatewayError("Persistent transient error")

    processor = DummyProcessor()
    with pytest.raises(AttemptPaymentError) as exc_info:
        processor.process_payment(mocker.Mock())
    assert exc_info.value.count == 2
    assert len(exc_info.value.errors) == 3
    assert exc_info.value.errors[-1] == "Max payment processing attempt limit reached: 2"
    assert all("Persistent transient error" in err for err in exc_info.value.errors[:-1])
