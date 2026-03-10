import re

with open("tests/test_fidelity_parser.py", "r") as f:
    content = f.read()

if 'import pandas as pd' not in content:
    content = 'import pandas as pd\n' + content

content = re.sub(r'transactions = parse\(temp_file\)', 'transactions = parse(pd.read_csv(temp_file))', content)

with open("tests/test_fidelity_parser.py", "w") as f:
    f.write(content)
