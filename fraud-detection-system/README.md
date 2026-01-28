# Fraud Detection System

- Data Validation (AbstractDataValidator)
    - Personal Information Validation (PersonalInfoDataValidator)
    - ACH Validation (routing, account number) (ACHDataValidator)
    - Credit Card Validation (name, cc number, expiration, cvv, zip) (CCDataValidator)

- Fraud Detection (AbstractFraudDetection)
    - IP Fraud Detection (IP Record, GeoIP location)
    - Fraud Record Detection (email, phone, financial institution)

- Account Status
    - Pending -> UNDER_REVIEW(Actions: Run Fraud Detection)
    - Declined -> REAPPLIED(Actions: Update Information, Run Fraud Detection)
    - Approved (Actions: Exit)


PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DECLINED = "declined"
    CLOSED = "closed"
    REAPPLIED = "reapplied"


Chain of Command
AbstractFactory
Builder?
State
Strategy
Template


