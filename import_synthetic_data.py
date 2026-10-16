"""Import the synthetic CSVs into credit_risk_project.

Append with: python import_synthetic_data.py
Replace this generator's reserved synthetic ID ranges with:
    python import_synthetic_data.py --replace-synthetic
"""

import argparse
import csv
import getpass
from pathlib import Path

import pymysql


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Dataset"
BATCH_SIZE = 1000

TABLES = [
    (
        "customers",
        DATA / "synthetic_customers.csv",
        ("customer_id", "name", "age", "income", "employment_type", "region"),
        "INSERT INTO customers (customer_id, name, age, income, employment_type, region) VALUES (%s, %s, %s, %s, %s, %s)",
        lambda row: (
            int(row["customer_id"]), row["name"], int(row["age"]),
            float(row["income"]), row["employment_type"], row["region"],
        ),
    ),
    (
        "loans",
        DATA / "synthetic_loans.csv",
        ("loan_id", "customer_id", "loan_amount", "interest_rate", "loan_purpose", "tenure_months", "loan_start_date"),
        "INSERT INTO loans (loan_id, customer_id, loan_amount, interest_rate, loan_purpose, tenure_months, loan_start_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        lambda row: (
            int(row["loan_id"]), int(row["customer_id"]), float(row["loan_amount"]),
            float(row["interest_rate"]), row["loan_purpose"], int(row["tenure_months"]),
            row["loan_start_date"],
        ),
    ),
    (
        "repayments",
        DATA / "synthetic_repayments.csv",
        ("repayment_id", "loan_id", "repayment_date", "amount_paid", "due_date"),
        "INSERT INTO repayments (repayment_id, loan_id, repayment_date, amount_paid, due_date) VALUES (%s, %s, %s, %s, %s)",
        lambda row: (
            int(row["repayment_id"]), int(row["loan_id"]), row["repayment_date"],
            float(row["amount_paid"]), row["due_date"],
        ),
    ),
]


def load_csv(cursor, table, path, expected_columns, insert_sql, convert_row):
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")

    count = 0
    batch = []
    with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if tuple(reader.fieldnames or ()) != expected_columns:
            raise ValueError(
                f"Unexpected columns in {path.name}: {reader.fieldnames}; "
                f"expected {list(expected_columns)}"
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                batch.append(convert_row(row))
            except (TypeError, ValueError, KeyError) as exc:
                raise ValueError(f"Invalid value in {path.name}, line {line_number}: {exc}") from exc

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(insert_sql, batch)
                count += len(batch)
                batch.clear()

        if batch:
            cursor.executemany(insert_sql, batch)
            count += len(batch)

    print(f"Prepared {count:,} rows for {table}.")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace-synthetic",
        action="store_true",
        help="delete only the reserved synthetic ID ranges, then reload the CSVs",
    )
    args = parser.parse_args()

    password = getpass.getpass("MySQL password for root: ")
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password=password,
        database="credit_risk_project",
        charset="utf8mb4",
        autocommit=False,
    )

    try:
        with connection.cursor() as cursor:
            if args.replace_synthetic:
                # Delete child rows before parent rows to preserve foreign keys.
                cursor.execute("DELETE FROM repayments WHERE repayment_id BETWEEN 100001 AND 180000")
                cursor.execute("DELETE FROM loans WHERE loan_id BETWEEN 10001 AND 20000")
                cursor.execute("DELETE FROM customers WHERE customer_id BETWEEN 5001 AND 10000")
                print("Removed rows from the reserved synthetic ID ranges.")
            counts = []
            # Parent rows first to satisfy the foreign-key constraints.
            for table, path, columns, insert_sql, convert_row in TABLES:
                counts.append(load_csv(cursor, table, path, columns, insert_sql, convert_row))
        connection.commit()
        print("Import committed successfully:")
        for (table, *_), count in zip(TABLES, counts):
            print(f"  {table}: {count:,} rows")
    except Exception:
        connection.rollback()
        print("Import failed; this run was rolled back.")
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
