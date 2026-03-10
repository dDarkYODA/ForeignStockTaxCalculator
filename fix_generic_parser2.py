import sys
import glob

def main():
    for f_path in glob.glob("backend/parsers/*.py"):
        with open(f_path, "r") as f:
            content = f.read()

        if "isinstance(df, str):" not in content:
            content = content.replace('df.columns = [str(c).strip() for c in df.columns]', 'if isinstance(df, str):\n        import pandas as pd\n        try:\n            df = pd.read_csv(df)\n        except:\n            df = pd.read_excel(df)\n    df.columns = [str(c).strip() for c in df.columns]')

            with open(f_path, "w") as f:
                f.write(content)

if __name__ == "__main__":
    main()
