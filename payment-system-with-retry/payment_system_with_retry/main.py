import argparse
from decimal import Decimal

from payment_system_with_retry.models import Payment
from payment_system_with_retry.payment_processors import register_state_payment_processors
from payment_system_with_retry.payment_service import PaymentProcessService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process a payment.")
    parser.add_argument("--state", type=str, required=True, help="State code for payment processing")
    parser.add_argument("--amount", type=Decimal, required=True, help="Payment amount")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    payment_processor_factory = register_state_payment_processors()

    payment = Payment(amount=args.amount)
    service = PaymentProcessService(
        payment_processor=payment_processor_factory.get_payment_processor(args.state)
    )
    processed_payment = service.process_payment(payment)
    if processed_payment.transaction:
        print(f"Payment Transaction ID: {processed_payment.transaction.transaction_id}")
        print(f"Payment Transaction Amount: {processed_payment.transaction.amount}")
    else:
        print("Payment Transaction Failed.")
        print(f"Payment Attempt Count: {processed_payment.attempt_count}")
        print(f"Payment Attempt Errors: {processed_payment.errors}")
