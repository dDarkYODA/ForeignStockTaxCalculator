import sys

def main():
    content = ""
    with open("backend/models/schema.py", "r") as f:
        content = f.read()

    # Add currency column to Lot model
    if "currency = Column(String)" not in content.split("class Lot(Base):")[1].split("class TaxCalculation(Base):")[0]:
        content = content.replace(
            "available_shares = Column(Float)",
            "available_shares = Column(Float)\n    currency = Column(String)"
        )

    with open("backend/models/schema.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
