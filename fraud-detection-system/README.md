# Fraud Detection System

This example project replicates a fraud detection system that validates user information and analyzes transactions for potential fraud. The system will use random dummy fraud scores to produce different results.

The system collects user input for personal information, device details, and payment methods (credit card or ACH), then runs fraud detection analysis to approve, decline, or request additional review.


## How to run
Run the main script in your CLI. The program will interactively prompt you for information:

```
python -m fraud_detection_system.main
```

The script will collect:
- Personal Information (name, age, SSN, phone, email)
- Device Information (IP address)
- Payment Method (Credit Card or ACH bank account details)
- Transaction Amount

Based on the inputs, the system will validate the data and perform fraud analysis, then provide next steps such as approve, decline, or reapply.

## Design Patterns
In this example python project I have used the following patterns

- **Data Validation** (AbstractDataValidator)
    - Personal Information Validation (PersonalInfoDataValidator)
    - ACH Validation (routing, account number) (ACHDataValidator)
    - Credit Card Validation (name, cc number, expiration, cvv, zip) (CCDataValidator)

- **Fraud Detection** (AbstractFraudDetection)
    - IP Fraud Detection (IP Record, GeoIP location)
    - Fraud Record Detection (email, phone, financial institution)

- **Account Status Management**
    - Pending → Under Review (Actions: Run Fraud Detection)
    - Declined → Reapplied (Actions: Update Information, Run Fraud Detection)
    - Approved (Actions: Exit)

Design patterns used:
1. State - To manage account status transitions
2. Strategy - To define common fraud detection operations
3. Template - For data validation workflows
4. Builder - To construct the applicable validations
5. Chain of responsibility - To manage the flow in fraud analysis 


