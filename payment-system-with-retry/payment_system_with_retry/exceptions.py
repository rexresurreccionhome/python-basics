

class RetryableError(Exception):
    """A dummy exception to simulate payment gateway errors."""
    pass


class DummyGatewayError(RetryableError):
    """A dummy exception to simulate transient errors."""
    pass


class AttemptPaymentError(Exception):
    _count: int
    _errors: list[str]
    """Custom exception for payment processing errors."""
    def __init__(self, count: int, errors: list[str]) -> None:
        self._count = count
        self._errors = errors
        super().__init__(f"An attempt to process payment has failed.")

    @property
    def count(self) -> int:
        return self._count

    @property
    def errors(self) -> list[str]:
        return self._errors
