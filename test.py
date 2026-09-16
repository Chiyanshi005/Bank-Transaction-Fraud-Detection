import unittest

from main import (
    validate_transaction,
    enhanced_validate_transaction,
    detect_high_value_transactions,
    detect_repeated_declines,
    detect_multiple_locations,
    read_transactions,
    detect_time_based_declines
)


class TestFraudDetection(unittest.TestCase):

    def test_valid_transaction(self):
        line = (
            "2026-07-11 09:15:23 | T2001 | A20001 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = validate_transaction(line)

        self.assertTrue(result)
        self.assertEqual(reason, "Valid")

    def test_incorrect_number_of_fields(self):
        line = (
            "2026-07-11 09:15:23 | T2002 | A20002 | "
            "TRANSFER | 850.00 | Brisbane"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Incorrect number of fields"
        )

    def test_invalid_transaction_type(self):
        line = (
            "2026-07-11 09:15:23 | T2003 | A20003 | "
            "INVALID_TYPE | 850.00 | Brisbane | APPROVED"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Invalid transaction type"
        )

    def test_invalid_status(self):
        line = (
            "2026-07-11 09:15:23 | T2004 | A20004 | "
            "TRANSFER | 850.00 | Brisbane | INVALID"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Invalid status"
        )

    def test_non_numeric_amount(self):
        line = (
            "2026-07-11 09:15:23 | T2005 | A20005 | "
            "TRANSFER | abc | Brisbane | APPROVED"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Amount is not numeric"
        )

    def test_zero_amount(self):
        line = (
            "2026-07-11 09:15:23 | T2006 | A20006 | "
            "TRANSFER | 0.00 | Brisbane | APPROVED"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Amount must be greater than zero"
        )

    def test_negative_amount(self):
        line = (
            "2026-07-11 09:15:23 | T2007 | A20007 | "
            "TRANSFER | -50.00 | Brisbane | APPROVED"
        )

        result, reason = validate_transaction(line)

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Amount must be greater than zero"
        )

    def test_high_value_transaction(self):
        transactions = [
            {
                "transaction_id": "T3001",
                "account_id": "A30001",
                "amount": 6500.00,
                "status": "APPROVED"
            }
        ]

        result = detect_high_value_transactions(transactions)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["transaction_id"],
            "T3001"
        )

    def test_repeated_declined_transactions(self):
        transactions = [
            {
                "transaction_id": "T3002",
                "account_id": "A30002",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T3003",
                "account_id": "A30002",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T3004",
                "account_id": "A30002",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T3005",
                "account_id": "A30002",
                "status": "DECLINED"
            }
        ]

        result = detect_repeated_declines(transactions)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["account_id"],
            "A30002"
        )
        self.assertEqual(
            result[0]["count"],
            4
        )

    def test_multiple_locations(self):
        transactions = [
            {
                "transaction_id": "T3006",
                "account_id": "A30003",
                "location": "Brisbane"
            },
            {
                "transaction_id": "T3007",
                "account_id": "A30003",
                "location": "Sydney"
            },
            {
                "transaction_id": "T3008",
                "account_id": "A30003",
                "location": "Melbourne"
            }
        ]

        result = detect_multiple_locations(transactions)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["account_id"],
            "A30003"
        )
        self.assertEqual(
            result[0]["location_count"],
            3
        )
    def test_normal_account_not_flagged(self):
        transactions = [
            {
                "transaction_id": "T4001",
                "account_id": "A40001",
                "amount": 500.00,
                "status": "APPROVED",
                "location": "Brisbane"
            },
            {
                "transaction_id": "T4002",
                "account_id": "A40001",
                "amount": 300.00,
                "status": "APPROVED",
                "location": "Brisbane"
            }
        ]

        high_value_result = detect_high_value_transactions(
            transactions
        )

        declined_result = detect_repeated_declines(
            transactions
        )

        location_result = detect_multiple_locations(
            transactions
        )

        self.assertEqual(len(high_value_result), 0)
        self.assertEqual(len(declined_result), 0)
        self.assertEqual(len(location_result), 0)
    def test_enhanced_valid_transaction(self):
        line = (
            "2026-07-11 09:15:23 | T5001 | A50001 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = enhanced_validate_transaction(
            line,
            set()
        )

        self.assertTrue(result)
        self.assertEqual(reason, "Valid")

    def test_invalid_timestamp(self):
        line = (
            "2026-99-99 09:15:23 | T5002 | A50002 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = enhanced_validate_transaction(
            line,
            set()
        )

        self.assertFalse(result)
        self.assertEqual(reason, "Invalid timestamp format")

    def test_invalid_transaction_id_format(self):
        line = (
            "2026-07-11 09:15:23 | TX001 | A50003 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = enhanced_validate_transaction(
            line,
            set()
        )

        self.assertFalse(result)
        self.assertEqual(reason, "Invalid transaction ID format")

    def test_invalid_account_id_format(self):
        line = (
            "2026-07-11 09:15:23 | T5004 | ACCOUNT1 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = enhanced_validate_transaction(
            line,
            set()
        )

        self.assertFalse(result)
        self.assertEqual(reason, "Invalid account ID format")

    def test_duplicate_transaction_id(self):
        line = (
            "2026-07-11 09:15:23 | T5005 | A50005 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        existing_ids = {"T5005"}

        result, reason = enhanced_validate_transaction(
            line,
            existing_ids
        )

        self.assertFalse(result)
        self.assertEqual(reason, "Duplicate transaction ID")

    def test_leading_whitespace(self):
        line = (
            " 2026-07-11 09:15:23 | T5006 | A50006 | "
            "TRANSFER | 850.00 | Brisbane | APPROVED"
        )

        result, reason = enhanced_validate_transaction(
            line,
            set()
        )

        self.assertFalse(result)
        self.assertEqual(
            reason,
            "Leading or trailing whitespace detected"
        )
    def test_missing_file(self):
        result = read_transactions("file_that_does_not_exist.txt")

        self.assertEqual(result, [])
    def test_empty_file(self):
        filename = "empty_test.txt"

        with open(filename, "w", encoding="utf-8") as file:
            file.write("")

        result = read_transactions(filename)

        self.assertEqual(result, [])
    def test_time_based_declined_transactions(self):
        transactions = [
            {
                "transaction_id": "T6001",
                "account_id": "A60001",
                "timestamp": "2026-07-11 09:00:00",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T6002",
                "account_id": "A60001",
                "timestamp": "2026-07-11 09:05:00",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T6003",
                "account_id": "A60001",
                "timestamp": "2026-07-11 09:10:00",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T6004",
                "account_id": "A60001",
                "timestamp": "2026-07-11 09:20:00",
                "status": "DECLINED"
            }
        ]

        result = detect_time_based_declines(transactions)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["account_id"], "A60001")
        self.assertEqual(result[0]["count"], 4)
    def test_normal_time_based_transactions_not_flagged(self):
        transactions = [
            {
                "transaction_id": "T7001",
                "account_id": "A70001",
                "timestamp": "2026-07-11 09:00:00",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T7002",
                "account_id": "A70001",
                "timestamp": "2026-07-11 09:05:00",
                "status": "DECLINED"
            },
            {
                "transaction_id": "T7003",
                "account_id": "A70001",
                "timestamp": "2026-07-11 09:10:00",
                "status": "DECLINED"
            }
        ]

        result = detect_time_based_declines(transactions)

        self.assertEqual(len(result), 0)
    def test_valid_transaction_file(self):
        result = read_transactions("transactions.txt")

        self.assertTrue(len(result) > 0)
        self.assertEqual(len(result), 16)
if __name__ == "__main__":
    unittest.main()