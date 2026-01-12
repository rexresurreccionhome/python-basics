from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PaymentTransaction:
    amount: Decimal = Decimal("0.00")
    transaction_id: str | None = None


@dataclass
class Payment:
    amount: Decimal
    attempt_count: int = 0
    errors: list[str] = field(default_factory=list)
    transaction: PaymentTransaction | None = None