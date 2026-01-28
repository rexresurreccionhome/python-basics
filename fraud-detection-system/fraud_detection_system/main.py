import sys

from fraud_detection_system.models import (
    PersonalInfo,
    DeviceInfo,
    CreditCard,
    BankAccount,
    PaymentMethodEnum,
    FraudRecord,
    Account,
)
from fraud_detection_system.fraud_detection_service import FraudDetectionService


def input_personal_info() -> PersonalInfo:
    print("Personal Information:")
    name = input("Enter Name: ")
    age = ""
    while True:
        age = input("Enter Age: ")
        if not age.isdigit():
            print("Invalid age. Please enter a numeric value.")
        else:
            break
    ssn = input("Enter SSN: ")
    phone_number = input("Enter Phone Number: ")
    email = input("Enter Email: ")
    personal_info = PersonalInfo(
        name=name,
        age=int(age),
        ssn=ssn,
        phone_number=phone_number,
        email=email,
    )
    return personal_info

def input_device_info() -> DeviceInfo:
    print("Device Information:")
    ip_address = input("Enter IP Address: ")
    return DeviceInfo(ip_address=ip_address)


def input_payment_method() -> tuple[PaymentMethodEnum, BankAccount | None, CreditCard | None]:
    payment_method = ""
    while True:
        payment_method = input("Enter Payment Method (CC or ACH): ").upper()
        if payment_method not in (PaymentMethodEnum.CREDIT_CARD, PaymentMethodEnum.ACH):
            print("Invalid payment method. Please select from CC or ACH.")
        else:
            break
    if payment_method == PaymentMethodEnum.CREDIT_CARD:
        print("Credit Card Information:")
        card_number = int(input("Enter Card Number: "))
        expiry_date = input("Enter Expiry Date (MM/YY): ")
        cvv = int(input("Enter CVV: "))
        zip_code = input("Enter Zip Code: ")
        credit_card = CreditCard(
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
            zip_code=zip_code,
        )
        return PaymentMethodEnum.CREDIT_CARD, None, credit_card
    else:
        print("Bank Account Information:")
        routing_number = int(input("Enter Routing Number: "))
        account_number = int(input("Enter Account Number: "))
        bank_account = BankAccount(
            routing_number=routing_number,
            account_number=account_number,
        )
        return PaymentMethodEnum.ACH, bank_account, None


def input_fraud_record() -> FraudRecord:
    print("Please provide the following fraud record details.")
    personal_info = input_personal_info()
    device_info = input_device_info()
    payment_method, bank_account, credit_card = input_payment_method()
    while True:
        amount_str = input("Enter Transaction Amount: ")
        try:
            amount = float(amount_str)
            break
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
    fraud_record = FraudRecord(
        amount=amount,
        personal_info=personal_info,
        device_info=device_info,
        payment_method=payment_method,
        bank_account=bank_account,
        credit_card=credit_card,
    )
    print("\nFraud Record Entered:")
    print(fraud_record)
    return fraud_record


def input_account_next_action(account_next_actions: tuple[str, ...]) -> str | None:
    if not account_next_actions:
        print("No further account actions.")
        return None
    
    print("Next Possible Actions:")
    for num, action in enumerate(account_next_actions):
        print(f"{num + 1}: {action}")
    
    while True:
        selected_action = input("Select action (default 1): ") or "1"
        if not selected_action.isdigit() or not (int(selected_action) in range(1, len(account_next_actions) + 1)):
            print("Invalid selection")
        else:
            break
    
    action = account_next_actions[int(selected_action) - 1]
    print(f"Selected Action: {action}")
    return action


def main():
    fraud_record = input_fraud_record()
    fraud_detection_service = FraudDetectionService()
    account = fraud_detection_service.review_fraud_record(
        account=Account(fraud_record=fraud_record)
    )
    while True:
        print(f"Data Validation Errors: {account.data_validation_errors}")
        print(f"Initial Account Status & Score: {account.status} | {account.fraud_score}")
        account_next_actions = fraud_detection_service.get_account_next_actions(account)
        action = input_account_next_action(account_next_actions)
        if action is None:
            break

        match action:
            case "reapply":
                fraud_record = input_fraud_record()
                account = fraud_detection_service.reapply_fraud_record(
                    account_id=account.account_id,
                    fraud_record=fraud_record
                )
            case "approve":
                account = fraud_detection_service.approve_fraud_record(account.account_id)
            case "decline":
                account = fraud_detection_service.decline_fraud_record(account.account_id)
            case _:
                print("Unknown action.")
                sys.exit(1)


if __name__ == "__main__":
    main()
