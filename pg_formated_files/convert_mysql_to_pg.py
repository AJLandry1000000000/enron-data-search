import re

def convert_mysql_to_postgres(mysql_file, postgres_file):
    """
    Converts a MySQL SQL file to PostgreSQL syntax and saves it to a new file.

    Args:
        mysql_file: Path to the input MySQL SQL file.
        postgres_file: Path to the output PostgreSQL SQL file.
    """
    with open(mysql_file, 'r') as f_in, open(postgres_file, 'w') as f_out:
        for line in f_in:
            # 1. Convert `AUTO_INCREMENT` to `SERIAL` and add `PRIMARY KEY`
            line = re.sub(r'`(\w+)`\s+int\(\d+\)\s+unsigned\s+NOT\s+NULL\s+AUTO_INCREMENT', r'\1 SERIAL PRIMARY KEY', line)

            # 2. Convert `TIMESTAMP` with `DEFAULT CURRENT_TIMESTAMP` to `TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
            line = re.sub(r'TIMESTAMP\s*DEFAULT\s*CURRENT_TIMESTAMP', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()', line)

            # 3. Convert `DATETIME` with `DEFAULT CURRENT_TIMESTAMP` to `TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
            line = re.sub(r'DATETIME\s*DEFAULT\s*CURRENT_TIMESTAMP', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()', line)

            # 4. Convert `TINYINT(1)` to `BOOLEAN`
            line = re.sub(r'TINYINT\(1\)', 'BOOLEAN', line)

            # 5. Convert `ENUM` to `VARCHAR` (adjust length as needed)
            line = re.sub(r'ENUM\(\'(.*?)\'\)', lambda m: "VARCHAR({})".format(len(m.group(1))), line)

            # 6. Remove `ENGINE=InnoDB` (PostgreSQL doesn't use it)
            line = re.sub(r'ENGINE=InnoDB', '', line)

            # 7. Remove `DEFAULT CHARSET=latin1` (PostgreSQL uses UTF-8 by default)
            line = re.sub(r'DEFAULT CHARSET=latin1', '', line)

            # 8. Handle potential issues (you might need to add more rules here)
            # ...
            # Replace MySQL comments (#) with PostgreSQL comments (--)
            line = re.sub(r'#', '--', line)

            # Replace backticks with double quotes
            line = re.sub(r'`', '"', line)

            # Remove MySQL-specific commands
            line = re.sub(r'SET SQL_MODE=.*?;\n', '', line)
            line = re.sub(r'SET FOREIGN_KEY_CHECKS=.*?;\n', '', line)
            line = re.sub(r'ENGINE=.*?;', '', line)

            # Remove double quotes around table and column names in CREATE TABLE statements
            line = re.sub(r'CREATE TABLE IF NOT EXISTS\s+"(\w+)"', r'CREATE TABLE IF NOT EXISTS \1', line)
            line = re.sub(r'"(\w+)"\s+(\w+)', r'\1 \2', line)

            # Remove PRIMARY KEY line if it exists
            line = re.sub(r',\s*PRIMARY KEY\s+\("(\w+)"\)', '', line)

            # Remove double quotes around table and column names in INSERT INTO statements
            line = re.sub(r'INSERT INTO\s+"(\w+)"\s+\((.*?)\)', lambda m: "INSERT INTO {} ({})".format(m.group(1), m.group(2).replace('"', '')), line)

            # Remove double quotes around column names in UNIQUE constraints
            line = re.sub(r'UNIQUE\s+KEY\s+"(\w+)"\s+\("(\w+)"\)', r'UNIQUE (\2)', line)
            line = re.sub(r'UNIQUE\s+\("(\w+)"\)', r'UNIQUE (\1)', line)

            f_out.write(line)


if __name__ == "__main__":
    mysql_file = "enron-mysqldump-adjusted.sql"
    postgres_file = "enron-mysqldump-adjusted_psql.sql"  # Updated output filename
    convert_mysql_to_postgres(mysql_file, postgres_file)
    print(f"MySQL to PostgreSQL conversion complete. Output saved to: {postgres_file}")