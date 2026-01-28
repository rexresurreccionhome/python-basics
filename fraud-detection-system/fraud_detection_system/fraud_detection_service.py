import re
import statistics
from abc import ABC
from typing import Self

from fraud_detection_system.database import DatabaseConnection
from fraud_detection_system.models import (
    Account,
    AccountStatusEnum,
    FraudRecord,
    PaymentMethodEnum,
)
from fraud_detection_system.validators import (
    DataValidatorBuilder,
    DataValidator,
    ValidationError,
)
from fraud_detection_system.fraud_analysis import FraudAnalysisService


class AccountContextError(Exception):
    pass


class AccountContext:
    _fraud_analysis_service: FraudAnalysisService
    _account: Account | None
    _account_state: "AccountState"

    def __init__(self, account: Account, fraud_analysis_service: FraudAnalysisService) -> None:
        self._fraud_analysis_service = fraud_analysis_service
        self._account = account
        self._initial_state()

    def _initial_state(self) -> None:
        state_map = {
            AccountStatusEnum.PENDING: PendingAccountState,
            AccountStatusEnum.REVIEWED: ReviewAccountState,
            AccountStatusEnum.APPROVED: ApproveAccountState,
            AccountStatusEnum.DECLINED: DeclineAccountState,
            AccountStatusEnum.REAPPLIED: ReapplyAccountState,
        }
        account_state_cls = state_map.get(self._account.status)
        if not account_state_cls:
            raise AccountContextError(f"Unknown account status: {self._account.status}")
        
        self._account_state = account_state_cls(self)
        self._account_state.next_state_on_success()

    @property
    def fraud_analysis_service(self) -> FraudAnalysisService:
        return self._fraud_analysis_service

    @property
    def account_state(self) -> "AccountState":
        return self._account_state

    @account_state.setter
    def account_state(self, account_state: "AccountState") -> None:
        self._account_state = account_state

    @property
    def account(self) -> Account | None:
        return self._account

    def update_account(self, status: AccountStatusEnum | None = None, analysis: dict[str, float] | None = None, validation_errors: list[ValidationError] | None = None) -> None:
        if status is not None:
            self._account.status = status
        if analysis is not None:
            self._account.fraud_score = round(statistics.mean(analysis.values()), 2) if analysis else 0.0
        if validation_errors is not None:
            self._account.data_validation_errors = [str(error) for error in validation_errors]
        # Publish updates to database or event bus here
    
    def do_review(self) -> None:
        if ReviewAccountState not in self.account_state.next_state_on_success():
            raise AccountContextError("Review action is currently not available")
        
        ReviewAccountState(self).review()

    def do_approve(self) -> None:
        if ApproveAccountState not in self.account_state.next_state_on_success():
            raise AccountContextError("Approve action is currently not available")
        
        ApproveAccountState(self).approve()

    def do_decline(self) -> None:
        if DeclineAccountState not in self.account_state.next_state_on_success():
            raise AccountContextError("Decline action is currently not available")
        
        DeclineAccountState(self).decline()

    def do_reapply(self) -> None:
        if ReapplyAccountState not in self.account_state.next_state_on_success():
            raise AccountContextError("Reapply action is currently not available")
        
        ReapplyAccountState(self).reapply()


class AccountState(ABC):
    def __init__(self, context: AccountContext) -> None:
        self._context = context
    
    @property
    def context(self) -> AccountContext:
        return self._context

    @staticmethod
    def next_state_on_success() -> tuple[type[Self], ...]:
        return tuple()

    def review(self) -> None:
        raise NotImplementedError("This account state does not support the review action")

    def approve(self) -> None:
        raise NotImplementedError("This account state does not support the approve action")

    def decline(self) -> None:
        raise NotImplementedError("This account state does not support the decline action")

    def reapply(self) -> None:
        raise NotImplementedError("This account state does not support the reapply action")


class PendingAccountState(AccountState):
    # A noop state, just to set the initial state
    @staticmethod
    def next_state_on_success() -> tuple[type[AccountState], ...]:
        return (ReviewAccountState,)


class ReviewAccountState(AccountState):
    def review(self) -> None:
        self.context.account_state = self
        validation_errors = self._run_data_validation()
        analysis = {}
        if not validation_errors:
            analysis = self.context.fraud_analysis_service.analyze_fraud_record(self.context.account.fraud_record)
            print(f"Fraud Analysis Results: {analysis}")
        
        self.context.update_account(status=AccountStatusEnum.REVIEWED, analysis=analysis, validation_errors=validation_errors)
        print("Processed to Reviewed State")

    @staticmethod
    def next_state_on_success() -> tuple[type[AccountState], ...]:
        return (ApproveAccountState, DeclineAccountState, ReapplyAccountState,)

    def _run_data_validation(self) -> list[ValidationError]:
        validators = self._build_data_validators()
        validation_errors = []
        for validator in validators:
            errors = validator.validate(self.context.account.fraud_record)
            validation_errors.extend(errors)

        return validation_errors

    def _build_data_validators(self) -> list[DataValidator]:
        validator_builder = DataValidatorBuilder()
        validator_builder.with_personal_info_validator()
        if self.context.account.fraud_record.payment_method is PaymentMethodEnum.CREDIT_CARD:
            validator_builder.with_credit_card_data_validator()
        elif self.context.account.fraud_record.payment_method is PaymentMethodEnum.ACH:
            validator_builder.with_ach_data_validator()
        
        return validator_builder.build_data_validators()


class ApproveAccountState(AccountState):
    def approve(self) -> None:
        self.context.account_state = self
        self.context.update_account(status=AccountStatusEnum.APPROVED)

    @staticmethod
    def next_state_on_success() -> tuple[type[AccountState], ...]:
        return tuple()


class DeclineAccountState(AccountState):
    def decline(self) -> None:
        self.context.account_state = self
        self.context.update_account(status=AccountStatusEnum.DECLINED)

    @staticmethod
    def next_state_on_success() -> tuple[type[AccountState], ...]:
        return (ReapplyAccountState,)


class ReapplyAccountState(AccountState):
    def reapply(self) -> None:
        self.context.account_state = self
        # Do some pre-review logic here
        self.context.update_account(status=AccountStatusEnum.REAPPLIED)
        print("Processed to Reapplied State")

    @staticmethod
    def next_state_on_success() -> tuple[type[AccountState], ...]:
        return (ReviewAccountState,)


class FraudDetectionService:
    _validator_builder: DataValidatorBuilder
    _database_connection: DatabaseConnection

    def __init__(
        self,
        fraud_analysis_service: FraudAnalysisService = FraudAnalysisService(),
        database_connection: DatabaseConnection = DatabaseConnection(),
    ) -> None:
        self._fraud_analysis_service = fraud_analysis_service
        self._database_connection = database_connection
    
    def _get_account(self, account_id: str) -> Account:
        return self._database_connection.get_fraud_record(account_id)
    
    def _store_account(self, account: Account) -> None:
        self._database_connection.store_fraud_record(account.account_id, account)
    
    def get_account_next_actions(self, account: Account) -> tuple[str, ...]:
        context = AccountContext(account, self._fraud_analysis_service)
        account_states = context.account_state.next_state_on_success()
        actions = []
        for account_state in account_states:
            if action_name := re.match(r'^[A-Z][a-z]*', account_state.__name__):
                actions.append(action_name.group().lower())
        
        return tuple(actions)

    def review_fraud_record(self, account: Account) -> Account:
        context = AccountContext(account, self._fraud_analysis_service)
        context.do_review()
        self._store_account(context.account)  # Store the fraud record in the dummy database
        return context.account

    def approve_fraud_record(self, account_id: str) -> Account:
        account = self._get_account(account_id)
        context = AccountContext(account, self._fraud_analysis_service)
        context.do_approve()
        self._store_account(context.account)
        return context.account

    def decline_fraud_record(self, account_id: str) -> Account:
        account = self._get_account(account_id)
        context = AccountContext(account, self._fraud_analysis_service)
        context.do_decline()
        self._store_account(context.account)
        return context.account
    
    def reapply_fraud_record(self, account_id: str, fraud_record: FraudRecord) -> Account:
        account = self._get_account(account_id)
        account.fraud_record = fraud_record
        context = AccountContext(account, self._fraud_analysis_service)
        context.do_reapply()
        self._store_account(context.account)
        return self.review_fraud_record(context.account)
