# Payment System With Retry

This example project replicates a payment system feature that has a retry mechanism.

The dummy payment processors will randomly fail to invoke a retry.

## Real World Scenario

The system acting as the payment processor will need to support bank transactions from different states.

An example would be: John Doe leaves in Illinois uses the system to submit his payment.

Scenario #1: The system was able to process the payment successfully.

Scenario #2: The system has got a retryable 503 error response from the bank. And the system has retried the request to the bank and eventually receives a successful response.

Scenario #3: The system has got a retryable 503 error response from the bank. And the system has retried the request multiple times but failed and eventually gives up.

Scenario #4: The system has got a 400 error response from the bank, due to an invalid payment information. And give up the process immediately.

## Design Patterns
In this example python project I have used the following patterns

1. Factory with Registry - To generate payment processor based on the value of `--state` argument. Also, a registry to add the supported payment processors.
2. Decorator - To implement the attempt to process payment with retry.
3. Strategy - To define the common operation(s) between payment processors. The service is acting as the Context that calls the expected method(s).

## How to run
Run the main script in your CLI

```
python -m payment_system_with_retry.main --state IL --amount 100.00
```

## Example Run With Successful Attempt
```
Payment Transaction ID: IL-12345
Payment Transaction Amount: 100.00
```

## Example Run With Multiple Failed Attempts
```
Payment Transaction Failed.
Payment Attempt Count: 3
Payment Attempt Errors: ['IL-001: Service Unavailable.', 'IL-001: Service Unavailable.', 'IL-001: Service Unavailable.', 'Max payment processing attempt limit reached: 3']
```
