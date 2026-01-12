import pytest

from payment_system_with_retry.exceptions import AttemptPaymentError
from payment_system_with_retry.models import PaymentTransaction
from payment_system_with_retry.payment_processors import(
    register_state_payment_processors,
    PaymentProcessorFactory,
    BankOfIllinoisPaymentProcessor,
    BankOfVirginiaPaymentProcessor,
    MAX_ATTEMPTS,
)


def test_register_state_payment_processors__registers_processors(mocker):
    register_state_payment_processors()
    il_processor = PaymentProcessorFactory.get_payment_processor("IL")
    assert isinstance(il_processor, BankOfIllinoisPaymentProcessor)
    va_processor = PaymentProcessorFactory.get_payment_processor("VA")
    assert isinstance(va_processor, BankOfVirginiaPaymentProcessor)


class TestPaymentProcessorFactory:
    def test_register_and_get_payment_processor__registers_processor(self):
        class DummyProcessor:
            pass

        PaymentProcessorFactory.register_payment_processor("XX", DummyProcessor)
        processor = PaymentProcessorFactory.get_payment_processor("XX")
        assert processor is DummyProcessor
    
    def test_get_payment_processor__unsupported_state__raises_value_error(self):
        with pytest.raises(ValueError) as exc_info:
            PaymentProcessorFactory.get_payment_processor("UnknownBank")
        assert str(exc_info.value) == "Unsupported bank: UnknownBank"


class TestBankOfIllinoisPaymentProcessor:
    def test_process_payment__success__returns_transaction(self, mocker):
        mocker.patch("payment_system_with_retry.payment_processors.choice", return_value=True)
        processor = BankOfIllinoisPaymentProcessor()
        transaction = processor.process_payment(mocker.Mock(amount=100.00))
        assert isinstance(transaction, PaymentTransaction)
    
    def test_process_payment__failure__raises_dummy_gateway_error(self, mocker):
        mocker.patch("payment_system_with_retry.payment_processors.choice", return_value=False)
        processor = BankOfIllinoisPaymentProcessor()
        with pytest.raises(AttemptPaymentError) as exc_info:
            processor.process_payment(mocker.Mock(amount=100.00))
        assert exc_info.value.count == MAX_ATTEMPTS


class TestBankOfVirginiaPaymentProcessor:
    def test_process_payment__success__returns_transaction(self, mocker):
        mocker.patch("payment_system_with_retry.payment_processors.choice", return_value=True)
        processor = BankOfVirginiaPaymentProcessor()
        transaction = processor.process_payment(mocker.Mock(amount=200.00))
        assert isinstance(transaction, PaymentTransaction)
    
    def test_process_payment__failure__raises_dummy_gateway_error(self, mocker):
        mocker.patch("payment_system_with_retry.payment_processors.choice", return_value=False)
        processor = BankOfVirginiaPaymentProcessor()
        with pytest.raises(AttemptPaymentError) as exc_info:
            processor.process_payment(mocker.Mock(amount=200.00))
        assert exc_info.value.count == MAX_ATTEMPTS
