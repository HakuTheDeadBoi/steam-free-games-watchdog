# Steam Free Games Watchdog

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A small Python script that monitors Steam and sends an email report of games with 100% discount.

---

## Features

- Fetches the list of free games from the [Steam Store](https://store.steampowered.com/)  
- Parses HTML and extracts games with 100% discount  
- Generates a readable text report  
- Sends the report via SMTP (supports multiple recipients)  
- Fully covered by unit tests (`unittest` + `mock`)  
- Can be scheduled to run automatically via GitHub Actions  

---

## Installation

1. Clone the repository:

```bash
git clone git@github.com:HakuTheDeadBoi/steam-free-games-watchdog.git
cd steam-free-games-watchdog
```

2. Recommended Python version: **3.14** (stdlib-only, no additional dependencies)

---

## Configuration

Set the following environment variables for SMTP:

| Variable     | Description |
|-------------|-------------|
| `RECIPIENTS` | Comma-separated list of email addresses |
| `SERVER`     | SMTP server |
| `PORT`       | SMTP port (e.g., 465) |
| `EMAIL`      | Sender's email address |
| `PASSWORD`   | Password or app-specific password |

Example:

```bash
export RECIPIENTS="me@example.com,you@example.com"
export SERVER="smtp.example.com"
export PORT="465"
export EMAIL="me@example.com"
export PASSWORD="secret"
```

---

## Usage

1. Run the script manually:

```bash
python -m run
```

2. Automatic execution via GitHub Actions:

- Cron schedule in `.github/workflows/run.yml`
- Use GitHub Secrets to store SMTP credentials

---

## Testing

Run all tests:

```bash
python -m unittest discover -s tests
```

Test coverage includes:  
- HTML parsing (all edge cases)  
- Report generation  
- SMTP sending (mocked)  
- Full pipeline (`main()` function)

---

## Project Structure

```
steam-free-games-watchdog/
├─ src/
│  ├─ main.py           # main script
├─ tests/
│  ├─ test_main.py      # unit tests
├─ .github/workflows/
│  ├─ run.yml           # GitHub Actions workflow
├─ .gitignore
├─ README.md
├─ LICENSE
├─ run.py               # entrypoint
```

---

## License

MIT License – feel free to copy and modify for your own use.

