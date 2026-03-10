import sys

def main():
    content = ""
    with open("tests/test_tax_engine.py", "r") as f:
        content = f.read()

    # The process_transactions is used in `calculate_gains(transactions)`
    content = content.replace("process_transactions(db)", "process_transactions(db, \"test\")")

    with open("tests/test_tax_engine.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
