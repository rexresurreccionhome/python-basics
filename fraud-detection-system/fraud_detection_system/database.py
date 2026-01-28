# This method will act as a dummy database by initializing an in-memory store using a dictionary.
import threading
from typing import Self

from fraud_detection_system.models import FraudRecord

class DatabaseConnection:
    _fraud_record_db: dict[str, FraudRecord] = {}
    _lock: threading.Lock = threading.Lock()
    _database_connection: Self | None = None

    def __new__(cls):
        with cls._lock:
            if cls._database_connection is None:
                cls._database_connection = super().__new__(cls) # calls parent object's __new__ method
        return cls._database_connection

    def get_fraud_record(self, account_id: str) -> FraudRecord:
        return self._fraud_record_db.get(account_id)

    def store_fraud_record(self, account_id: str, fraud_record: FraudRecord) -> None:
        self._fraud_record_db[account_id] = fraud_record

