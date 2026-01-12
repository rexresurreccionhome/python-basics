
from typing import Callable
from functools import wraps

from payment_system_with_retry.exceptions import (
    RetryableError,
    AttemptPaymentError,
)
from payment_system_with_retry.models import (
    Payment,
    PaymentTransaction,
)


def attempt_payment_decorator(*, retry_exceptions: tuple[type[RetryableError], ...], max_attempts: int = 1) -> Callable:
    """
    This decorator would retry transient errors during payment processing up to a maximum number of attempts.
    An error will be raised if all attempts to process the payment fail.
    """ 
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1") # Sanity check
    
    def decorator(process_payment: Callable) -> Callable:
        @wraps(process_payment)
        def wrapper(self, payment: Payment) -> PaymentTransaction:
            process_payment_counter = 0
            errors = []
            transaction = None
            while process_payment_counter < max_attempts:
                try:
                    process_payment_counter += 1
                    transaction = process_payment(self, payment)
                    break  # Exit loop on success
                except retry_exceptions as error:
                    errors.append(str(error))
                    if process_payment_counter >= max_attempts:
                        errors.append(f"Max payment processing attempt limit reached: {max_attempts}")
                except Exception as error:
                    # For any other non-transient errors, we stop retrying
                    errors.append(str(error))
                    errors.append(f"An unexpected error occurred. Stopping retries.")
                    raise AttemptPaymentError(
                        process_payment_counter,
                        errors,
                    )
            if transaction is None:
                raise AttemptPaymentError(
                    process_payment_counter,
                    errors,
                )
            return transaction
        return wrapper
    return decorator
