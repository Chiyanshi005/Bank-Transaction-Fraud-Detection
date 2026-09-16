# Bank Transaction Fraud Detection

## Project Overview

This project is a Python-based Bank Transaction Fraud Detection System. It processes fictional bank transaction records, validates the data and identifies potentially suspicious transactions or accounts using rule-based fraud detection.

## Features

- Reads transactions from a text file
- Validates transaction records
- Rejects invalid records with reasons
- Stores valid transactions using Python data structures
- Detects high-value transactions
- Detects repeated declined transactions
- Detects transactions across multiple locations
- Performs enhanced data validation
- Detects time-based suspicious activity
- Includes automated testing using Python unittest

## Fraud Detection Rules

### Rule 1 – High-Value Transactions

Flags approved transactions with an amount greater than $5,000.

### Rule 2 – Repeated Declined Transactions

Flags accounts with four or more declined transactions.

### Rule 3 – Multiple Locations

Flags accounts with transactions across three or more different locations.

### Advanced Rule – Time-Based Detection

Flags accounts with four or more declined transactions within a 30-minute period.

## Enhanced Data Validation

The system validates:

- Timestamp format
- Transaction ID format
- Account ID format
- Transaction type
- Transaction amount
- Location
- Transaction status
- Duplicate transaction IDs
- Leading or trailing whitespace

## Project Files

| File | Description |
|------|-------------|
| `main.py` | Main fraud detection program |
| `test.py` | Automated test cases |
| `transactions.txt` | Fictional transaction dataset |

## How to Run

Make sure Python is installed, then run:

```bash
python main.py

To run the automated tests:

python test.py
Testing

The project includes 22 automated test cases covering valid transactions, invalid input, file handling, fraud detection rules and advanced features.

Final test execution:

Ran 22 tests in 0.009s

OK

The main program processed 16 transaction records, accepting 13 valid records and rejecting 3 invalid records.

Technologies Used
Python
Python Standard Library
re
datetime
unittest
Disclaimer

This project uses fictional transaction data and is developed for educational and assessment purposes. It is not intended for use as a production banking fraud detection system.
