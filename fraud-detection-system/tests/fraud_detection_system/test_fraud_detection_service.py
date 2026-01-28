import pytest

from fraud_detection_system.models import Account, AccountStatusEnum
from fraud_detection_system.fraud_analysis import FraudAnalysisService
from fraud_detection_system.fraud_detection_service import (
    PendingAccountState,
    AccountContext,
    ReviewAccountState,
    AccountContextError,
)
from tests.fraud_detection_system.builder import FraudRecordBuilder


class TestAccountContext:
    def test_fraud_analysis_service__mock_fraud_analysis_service__returns_mocked_service(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        assert fraud_detection_service.fraud_analysis_service is mock_fraud_analysis_service
    
    def test_account_state__pending_account_state__returns_pending_state(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        assert isinstance(fraud_detection_service.account_state, PendingAccountState)
    
    def test_account_state_setter__set_review_state__updates_account_state(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        class MockAccountState:
            pass
        mock_account_state = MockAccountState()
        fraud_detection_service.account_state = mock_account_state
        assert fraud_detection_service.account_state is mock_account_state
    
    def test_account__pending_account__returns_account(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        assert fraud_detection_service.account is account
    
    def test_update_account__update_status_and_analysis_and_validation_errors__updates_account(
        self, mocker
    ):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        fraud_detection_service.update_account(
            status=AccountStatusEnum.REVIEWED,
            analysis={"fraud_score": 75.0},
            validation_errors=["error1", "error2"]
        )
        assert fraud_detection_service.account.status is AccountStatusEnum.REVIEWED
        assert fraud_detection_service.account.fraud_score == 75.0
        assert fraud_detection_service.account.data_validation_errors == ["error1", "error2"]
    
    def test_do_review__mock_review_account_state__review_account_state_do_review_called(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        mock_review_account_state = mocker.Mock(spec=ReviewAccountState)
        mocker.patch("fraud_detection_system.fraud_detection_service.ReviewAccountState", new=mock_review_account_state)
        mock_account_state = mocker.Mock()
        mock_account_state.next_state_on_success.return_value = (mock_review_account_state,)
        fraud_detection_service.account_state = mock_account_state
        fraud_detection_service.do_review()
        mock_review_account_state.return_value.review.assert_called_once()
    
    def test_do_review__review_account_state_not_in_next_state_on_success__raise_account_context_error(self, mocker):
        mock_fraud_analysis_service = mocker.Mock(spec=FraudAnalysisService)
        account = Account(fraud_record=FraudRecordBuilder().build())
        fraud_detection_service = AccountContext(
            account=account,
            fraud_analysis_service=mock_fraud_analysis_service
        )
        mock_account_state = mocker.Mock()
        mock_account_state.next_state_on_success.return_value = tuple()
        fraud_detection_service.account_state = mock_account_state
        with pytest.raises(AccountContextError):
            fraud_detection_service.do_review()