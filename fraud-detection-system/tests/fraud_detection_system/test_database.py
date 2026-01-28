from fraud_detection_system.database import DatabaseConnection
from tests.fraud_detection_system.builder import FraudRecordBuilder


class TestDatabaseConnection:
    def test_singleton__initialize_multiple_instances__produces_same_instance(self):
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        assert db1 is db2
    
    def test_store_and_get_fraud_record__add_new_record__returns_record(self):
        fraud_record = FraudRecordBuilder().build()
        db = DatabaseConnection()
        db.store_fraud_record(account_id="acct_123", fraud_record=fraud_record)
        retrieved_record = db.get_fraud_record(account_id="acct_123")
        assert retrieved_record == fraud_record
