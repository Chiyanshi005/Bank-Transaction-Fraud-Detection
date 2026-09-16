import re
from datetime import datetime

VALID_TRANSACTION_TYPES = {
    "TRANSFER",
    "CARD_PAYMENT",
    "CASH_WITHDRAWAL",
    "ONLINE_PURCHASE",
    "DIRECT_DEBIT"
}

VALID_STATUSES = {
    "APPROVED",
    "DECLINED",
    "PENDING"
}


def validate_transaction(line):
    """Validate a single transaction record."""
    fields = [field.strip() for field in line.split("|")]

    if len(fields) != 7:
        return False, "Incorrect number of fields"

    (
        timestamp,
        transaction_id,
        account_id,
        transaction_type,
        amount,
        location,
        status
    ) = fields

    if not transaction_id:
        return False, "Transaction ID is empty"

    if not account_id:
        return False, "Account ID is empty"

    if transaction_type not in VALID_TRANSACTION_TYPES:
        return False, "Invalid transaction type"

    if status not in VALID_STATUSES:
        return False, "Invalid status"

    try:
        amount = float(amount)
    except ValueError:
        return False, "Amount is not numeric"

    if amount <= 0:
        return False, "Amount must be greater than zero"

    if not location:
        return False, "Location is empty"

    return True, "Valid"

def enhanced_validate_transaction(line, transaction_ids):
    """Perform enhanced validation on a transaction record."""

    # Check for leading or trailing whitespace
    if line != line.strip():
        return False, "Leading or trailing whitespace detected"

    fields = [field.strip() for field in line.split("|")]

    # Check number of fields
    if len(fields) != 7:
        return False, "Incorrect number of fields"

    (
        timestamp,
        transaction_id,
        account_id,
        transaction_type,
        amount,
        location,
        status
    ) = fields

    # Check timestamp format
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False, "Invalid timestamp format"

    # Check transaction ID format
    if not re.fullmatch(r"T\d{4}", transaction_id):
        return False, "Invalid transaction ID format"

    # Check account ID format
    if not re.fullmatch(r"A\d{5}", account_id):
        return False, "Invalid account ID format"

    # Check transaction type
    if transaction_type not in VALID_TRANSACTION_TYPES:
        return False, "Invalid transaction type"

    # Check status
    if status not in VALID_STATUSES:
        return False, "Invalid status"

    # Check amount
    if not re.fullmatch(r"\d+(\.\d{1,2})?", amount):
        return False, "Amount must be numeric with up to two decimal places"

    try:
        amount_value = float(amount)
    except ValueError:
        return False, "Amount is not numeric"

    if amount_value <= 0:
        return False, "Amount must be greater than zero"
    # Check location
    if not location:
        return False, "Location is empty"

    # Check duplicate transaction ID
    if transaction_id in transaction_ids:
        return False, "Duplicate transaction ID"

    return True, "Valid"
def detect_high_value_transactions(transactions):
    """Detect approved transactions above $5,000."""
    suspicious_transactions = []

    for transaction in transactions:
        if (
            transaction["status"] == "APPROVED"
            and transaction["amount"] > 5000
        ):
            suspicious_transactions.append(transaction)

    return suspicious_transactions
def detect_repeated_declines(transactions):
    """Detect accounts with four or more declined transactions."""
    declined_by_account = {}

    for transaction in transactions:
        if transaction["status"] == "DECLINED":
            account_id = transaction["account_id"]

            if account_id not in declined_by_account:
                declined_by_account[account_id] = []

            declined_by_account[account_id].append(
                transaction["transaction_id"]
            )

    suspicious_accounts = []

    for account_id, transaction_ids in declined_by_account.items():
        if len(transaction_ids) >= 4:
            suspicious_accounts.append({
                "account_id": account_id,
                "count": len(transaction_ids),
                "transaction_ids": transaction_ids
            })

    return suspicious_accounts
def detect_multiple_locations(transactions):
    """Detect accounts with transactions in three or more locations."""
    locations_by_account = {}

    for transaction in transactions:
        account_id = transaction["account_id"]

        if account_id not in locations_by_account:
            locations_by_account[account_id] = {}

        location = transaction["location"]
        transaction_id = transaction["transaction_id"]

        if location not in locations_by_account[account_id]:
            locations_by_account[account_id][location] = []

        locations_by_account[account_id][location].append(
            transaction_id
        )

    suspicious_accounts = []

    for account_id, locations in locations_by_account.items():
        if len(locations) >= 3:
            transaction_ids = []

            for ids in locations.values():
                transaction_ids.extend(ids)

            suspicious_accounts.append({
                "account_id": account_id,
                "location_count": len(locations),
                "locations": list(locations.keys()),
                "transaction_ids": transaction_ids
            })

    return suspicious_accounts
def detect_time_based_declines(transactions):
    """Detect four or more declines within 30 minutes."""
    suspicious_accounts = []

    accounts = {}

    for transaction in transactions:
        account_id = transaction["account_id"]

        if account_id not in accounts:
            accounts[account_id] = []

        if transaction["status"] == "DECLINED":
            accounts[account_id].append(transaction)

    for account_id, declined_transactions in accounts.items():
        declined_transactions.sort(
            key=lambda transaction: datetime.strptime(
                transaction["timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )
        )

        for i in range(len(declined_transactions)):
            start_time = datetime.strptime(
                declined_transactions[i]["timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )

            matching_transactions = []

            for j in range(i, len(declined_transactions)):
                current_time = datetime.strptime(
                    declined_transactions[j]["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                difference = current_time - start_time

                if difference.total_seconds() <= 1800:
                    matching_transactions.append(
                        declined_transactions[j]["transaction_id"]
                    )

            if len(matching_transactions) >= 4:
                suspicious_accounts.append({
                    "account_id": account_id,
                    "count": len(matching_transactions),
                    "transaction_ids": matching_transactions
                })
                break

    return suspicious_accounts
def read_transactions(filename):
    """Read transaction records from a text file."""
    transactions = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if not lines:
            print("Error: The transaction file is empty.")
            return []

        for line in lines[1:]:
            line = line.strip()

            if line:
                transactions.append(line)

        return transactions

    except FileNotFoundError:
        print(f"Error: File '{filename}' was not found.")
        return []

    except OSError:
        print(f"Error: Unable to read file '{filename}'.")
        return []


def main():
    filename = "transactions.txt"

    transactions = read_transactions(filename)

    if not transactions:
        return

    valid_transactions = []
    transaction_ids = set()

    for line_number, line in enumerate(transactions, start=2):
        is_valid, reason = enhanced_validate_transaction(
    line,
    transaction_ids
)

        if is_valid:
            fields = [field.strip() for field in line.split("|")]

            transaction = {
                "timestamp": fields[0],
                "transaction_id": fields[1],
                "account_id": fields[2],
                "transaction_type": fields[3],
                "amount": float(fields[4]),
                "location": fields[5],
                "status": fields[6]
            }

            valid_transactions.append(transaction)
            transaction_ids.add(transaction["transaction_id"])

        else:
            print(
                f"Line {line_number} rejected: {reason}"
            )

    print(f"\nValid transactions: {len(valid_transactions)}")
    print(
        f"Invalid transactions: "
        f"{len(transactions) - len(valid_transactions)}"
    )

    # Rule 1: High-Value Transactions
    high_value_transactions = detect_high_value_transactions(
        valid_transactions
    )

    print("\n--- Rule 1: High-Value Transactions ---")

    if high_value_transactions:
        for transaction in high_value_transactions:
            print(
                f"Transaction ID: "
                f"{transaction['transaction_id']}"
            )
            print(
                f"Account ID: "
                f"{transaction['account_id']}"
            )
            print(
                f"Amount: "
                f"${transaction['amount']:.2f}"
            )
            print(
                "Detection Rule: "
                "High-Value Transaction"
            )
            print(
                f"Reason: Approved amount of "
                f"${transaction['amount']:.2f} exceeded "
                f"the $5,000 threshold."
            )
            print()
    else:
        print("No high-value transactions detected.")

        # Rule 2: Repeated Declined Transactions
    repeated_declines = detect_repeated_declines(
        valid_transactions
    )

    print("\n--- Rule 2: Repeated Declined Transactions ---")

    if repeated_declines:
        for account in repeated_declines:
            print(
                f"Account ID: {account['account_id']}"
            )
            print(
                f"Number of declined transactions: "
                f"{account['count']}"
            )
            print(
                f"Relevant Transaction IDs: "
                f"{', '.join(account['transaction_ids'])}"
            )
            print(
                "Detection Rule: "
                "Repeated Declined Transactions"
            )
            print(
                f"Reason: Account {account['account_id']} "
                f"had {account['count']} declined transactions."
            )
            print()
    else:
        print("No accounts with repeated declined transactions.")

        # Rule 3: Multiple Locations
    multiple_locations = detect_multiple_locations(
        valid_transactions
    )

    print("\n--- Rule 3: Multiple Locations ---")

    if multiple_locations:
        for account in multiple_locations:
            print(
                f"Account ID: {account['account_id']}"
            )
            print(
                f"Number of different locations: "
                f"{account['location_count']}"
            )
            print(
                f"Locations involved: "
                f"{', '.join(account['locations'])}"
            )
            print(
                f"Relevant Transaction IDs: "
                f"{', '.join(account['transaction_ids'])}"
            )
            print(
                "Detection Rule: Multiple Locations"
            )
            print(
                f"Reason: Account {account['account_id']} "
                f"had transactions in "
                f"{account['location_count']} different locations."
            )
            print()
    else:
        print("No accounts with multiple locations detected.")
        # Advanced Feature 2: Time-Based Fraud Detection
    time_based_declines = detect_time_based_declines(
        valid_transactions
    )

    print("\n--- Advanced Feature 2: Time-Based Declines ---")

    if time_based_declines:
        for account in time_based_declines:
            print(f"Account ID: {account['account_id']}")
            print(
                f"Number of declined transactions within 30 minutes: "
                f"{account['count']}"
            )
            print(
                f"Relevant Transaction IDs: "
                f"{', '.join(account['transaction_ids'])}"
            )
            print(
                "Detection Rule: "
                "Four or More Declined Transactions Within 30 Minutes"
            )
            print(
                f"Reason: Account {account['account_id']} had "
                f"{account['count']} declined transactions "
                f"within a 30-minute period."
            )
            print()
    else:
        print(
            "No accounts with four or more declined transactions "
            "within 30 minutes."
        )
if __name__ == "__main__":
    main()