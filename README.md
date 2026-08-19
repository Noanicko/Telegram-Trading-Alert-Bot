[README.md](https://github.com/user-attachments/files/31223181/README.md)
# Forex Wickless Candle Telegram Alert Bot

A lightweight Python bot that monitors live forex candle data from Dukascopy and sends Telegram notifications when a completed 15-minute candle has no lower wick (bullish) or no upper wick (bearish).

The bot can watch multiple currency pairs concurrently, restrict alerts to configured trading sessions, skip market holidays, and automatically reconnect after a stream error.

> [!WARNING]
> This project is intended for educational and analytical purposes only. It is not financial advice and does not place trades. Market data can be delayed, incomplete, or incorrect. Validate every signal independently before making financial decisions.

## Features

- Streams live 15-minute forex candles from Dukascopy.
- Watches multiple currency pairs in parallel using threads.
- Detects bullish candles with no lower wick (`open == low`).
- Detects bearish candles with no upper wick (`open == high`).
- Sends alerts through the Telegram Bot API.
- Restricts processing to a configurable trading session.
- Skips configured holidays.
- Retries automatically when a market-data stream fails.
- Keeps credentials outside the source code through environment variables.

## Project structure

```text
.
├── config.py                    # Runtime settings and environment-variable loading
├── main.py                      # Main application entry point
├── telegram_functionality.py    # Telegram messaging helpers
├── threading_function.py        # Creates one monitoring thread per configured pair
├── trade_logic.py               # Candle evaluation and signal logic
├── .env.example                 # Safe configuration template
├── .gitignore                   # Excludes secrets and generated files
└── README.md
```

`main.py` is the only application entry point. Runtime settings live in `config.py`, worker creation is handled by `threading_function.py`, market-data processing lives in `trade_logic.py`, and Telegram delivery is isolated in `telegram_functionality.py`.

## How it works

1. The application loads configuration and Telegram credentials.
2. `main.py` passes its thread list to `threading_function.threading()`.
3. The helper starts one daemon thread per pair in `config.WATCHED_PAIRS`, with `trade_logic.monitor_pair()` as its target.
4. Each worker opens a live Dukascopy stream for 15-minute candles.
5. Updates for the active candle are stored until a newer candle appears.
6. The completed candle is checked against the configured session and holiday rules.
7. A Telegram alert is sent when the completed candle matches the wickless-candle condition.
8. If a stream crashes, the worker waits three seconds and reconnects.

### Signal definitions

| Signal | Condition | Meaning |
| --- | --- | --- |
| Bullish wickless candle | `close > open` and `open == low` | The candle has no lower wick |
| Bearish wickless candle | `close <= open` and `open == high` | The candle has no upper wick |

Floating-point market data can contain tiny rounding differences. If exact comparisons prove unreliable, use a tolerance such as `math.isclose()` instead of `==`.

## Requirements

- Python 3.10 or newer
- A Telegram account
- A Telegram bot token created with [BotFather](https://t.me/BotFather)
- The target Telegram user, group, or channel chat ID
- Internet access to Dukascopy and Telegram

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If the repository contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the packages directly:

```bash
pip install dukascopy-python pandas requests python-dotenv
```

You can then create a reproducible dependency file:

```bash
pip freeze > requirements.txt
```

## Configuration

### 1. Create the environment file

Copy the example file:

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Use this structure in `.env.example`:

```dotenv
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

Then add the real values only to your local `.env` file:

```dotenv
TELEGRAM_TOKEN=replace_with_your_bot_token
TELEGRAM_CHAT_ID=replace_with_your_chat_id
```

### 2. Load secrets in `config.py`

```python
import os
from datetime import datetime, time

import dukascopy_python as dk
from dotenv import load_dotenv
from dukascopy_python.instruments import (
    INSTRUMENT_FX_MAJORS_AUD_USD,
    INSTRUMENT_FX_MAJORS_GBP_USD,
    INSTRUMENT_FX_MAJORS_USD_JPY,
)

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

END = None
OFFER_SIDE = dk.OFFER_SIDE_BID
SESSION_STARTTIME = time(7, 30)
SESSION_ENDTIME = time(18, 0)

WATCHED_PAIRS = [
    ("USD-JPY", INSTRUMENT_FX_MAJORS_USD_JPY),
    ("AUD-USD", INSTRUMENT_FX_MAJORS_AUD_USD),
    ("GBP-USD", INSTRUMENT_FX_MAJORS_GBP_USD),
]

HOLIDAYS = {
    datetime(2026, 1, 1).date(),
    # Add every date on which this strategy should remain inactive.
}
```

Using `os.environ[...]` makes the program fail immediately with a clear error when a required secret is missing. For optional values, use `os.getenv("NAME", "default")` instead. A `set` is recommended for `HOLIDAYS` because the application repeatedly performs membership checks.

The current project holiday list contains only 2024 and 2025 dates. Update it for the current year before running the bot. Holiday calendars also differ across currencies and venues, so a single US/UK list may not match every monitored pair.

### 3. Protect secrets

Ensure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.idea/
.vscode/
```

Never commit `.env`, API tokens, chat credentials, or private keys. If a token has ever appeared in source code, an issue, a screenshot, or Git history, revoke it and generate a new one. Removing the text from the latest commit does not invalidate an exposed token.

For production deployments, store secrets in the deployment platform's secret manager rather than committing or uploading an `.env` file.

## Telegram setup

1. Open [BotFather](https://t.me/BotFather) in Telegram.
2. Run `/newbot` and follow the prompts.
3. Store the generated token in `TELEGRAM_TOKEN`.
4. Add the bot to the target group or channel.
5. Give it permission to post messages when using a channel.
6. Store the target chat ID in `TELEGRAM_CHAT_ID`.

For private chats, send the bot a message before testing. Group and channel IDs commonly begin with `-100`, but always use the exact ID returned for your target chat.

## Selecting currency pairs

The monitored instruments are configured in `config.py`:

```python
WATCHED_PAIRS = [
    ("USD-JPY", INSTRUMENT_FX_MAJORS_USD_JPY),
    ("AUD-USD", INSTRUMENT_FX_MAJORS_AUD_USD),
    ("GBP-USD", INSTRUMENT_FX_MAJORS_GBP_USD),
]
```

Add or remove entries using instrument constants provided by `dukascopy_python.instruments`.

## Running the bot

Start the documented entry point:

```bash
python main.py
```

Expected startup output resembles:

```text
Bot is running on 3 pairs. Press Ctrl+C to stop.
```

The bot also sends a Telegram startup message. Stop it with `Ctrl+C`.

## Example alerts

```text
📈 🟢 Wickless Candle on USD-JPY at 19.08 14:15
```

```text
📉 🔴 Wickless Candle on GBP-USD at 19.08 14:30
```

The current implementation always sends a second “Normal” message containing the candle's open, high, low, and close values—even when it has already sent a wickless alert. Remove or guard that block if you only want signal notifications.

## Important implementation notes

### Completed candles only

The stream can publish several updates for the same active candle. The bot retains the most recent update and evaluates that candle only after a newer timestamp arrives. This prevents alerts based on an unfinished candle.

Because out-of-session updates are skipped before `pending_candle` is advanced, the last in-session candle can remain pending until the next in-session update. Review this behavior if you do not want a previous session's final candle evaluated when the next session begins.

### Time zones

Keep the following time zones explicit and consistent:

- The timestamps returned by Dukascopy
- `SESSION_STARTTIME` and `SESSION_ENDTIME`
- The time displayed in Telegram messages
- The machine or container running the bot

Avoid applying a fixed offset such as `timedelta(hours=1)` unless the source timezone and daylight-saving behavior are known. Prefer timezone-aware `datetime` values using Python's `zoneinfo` module.

### Network requests

The current `send_telegram()` catches connection exceptions, but it does not set a timeout or treat Telegram HTTP error responses as failures. A safer implementation is:

```python
response = requests.get(
    url,
    params={"chat_id": TELEGRAM_CHAT_ID, "text": message},
    timeout=15,
)
response.raise_for_status()
```

For production use, add bounded retries with exponential backoff so temporary Telegram failures do not silently discard alerts.

### Thread behavior

Each currency pair runs in a daemon thread created by `threading_function.threading()`. An unhandled failure in one thread should not stop the others, but daemon threads are terminated when the main process exits. For graceful shutdowns and larger deployments, consider a shared `threading.Event` and non-daemon workers.

The helper name `threading()` is easy to confuse with Python's `threading` module. A clearer name would be `start_monitor_threads()`.

## Troubleshooting

### `NameError: name 'OFFER_SIDE' is not defined`

Confirm the variable exists at module level in `config.py`. Prefer explicit module imports:

```python
import config as cfg

print(cfg.OFFER_SIDE)
```

Also verify which file Python imported:

```python
import config
print(config.__file__)
```

### `KeyError: 'TELEGRAM_TOKEN'`

The environment variable is missing. Confirm that:

- `.env` exists in the directory from which the application is launched.
- The variable name is spelled exactly as expected.
- `load_dotenv()` runs before `os.environ[...]` is accessed.

### Telegram returns `401 Unauthorized`

The bot token is invalid or has been revoked. Generate a new token with BotFather and update the environment variable.

### Telegram returns `400 Bad Request: chat not found`

Verify the chat ID, start a private conversation with the bot, or add the bot to the target group/channel and grant the required permissions.

### No signals appear

Check that:

- The current time falls inside the configured session.
- Today's date is not in `HOLIDAYS`.
- The selected instruments are supported.
- Candle timestamps use the timezone you expect.
- The market is open and Dukascopy is returning data.
- Exact `open == low` or `open == high` comparisons are appropriate for the returned price precision.

### Duplicate or excessive messages

The current logic sends both a wickless alert and a normal-candle message for the same qualifying candle. Remove or disable the normal-candle notification block if only signal alerts are desired.

### Alerts arrive at the wrong time

`trade_logic.py` currently displays candle times by adding a fixed one-hour offset. This does not automatically account for daylight-saving changes. Confirm the Dukascopy timestamp timezone, then convert with `zoneinfo.ZoneInfo` instead of using a fixed `timedelta`.

Also ensure that `SESSION_STARTTIME = time(7, 30)` and `SESSION_ENDTIME = time(18, 0)` are expressed in the same timezone as `timestamp.time()`.

### Bot runs, but holiday filtering is wrong

The supplied `HOLIDAYS` list ends in 2025. Add the required 2026 and later dates, or generate them through a maintained market-calendar source. Currency markets do not necessarily close for every US or UK holiday in the same way.

## Testing

Before leaving the bot unattended:

1. Test Telegram delivery with a harmless startup message.
2. Run one currency pair during an active market session.
3. Log candle timestamps and OHLC values.
4. Confirm that only completed candles are evaluated.
5. Simulate a stream exception and verify reconnection.
6. Confirm session boundaries and holiday filtering.
7. Compare detected signals against an independent chart.

Good unit-test targets include:

- Bullish and bearish wickless detection
- Doji handling (`open == close`)
- Floating-point tolerance
- Session start and end boundaries
- Holiday exclusion
- Candle rollover behavior
- Telegram failures and retry behavior

## Suggested improvements

- Move all signal evaluation into pure functions in `trade_logic.py`.
- Keep Telegram HTTP code isolated in `telegram_functionality.py`.
- Replace wildcard imports with explicit module imports.
- Rename `threading_function.threading()` to `start_monitor_threads()`.
- Remove unused imports and the unused `START` configuration value.
- Update or generate the holiday calendar for every active year.
- Add structured logging instead of relying only on `print()`.
- Add type hints and automated tests with `pytest`.
- Add formatting and linting with Ruff.
- Add a graceful shutdown event for worker threads.
- Add rate limiting, retry backoff, and alert deduplication.
- Pin dependency versions in `requirements.txt` or `pyproject.toml`.
- Add a Dockerfile or service definition for reliable deployment.

## Security checklist

- [ ] `.env` is excluded by `.gitignore`.
- [ ] No real secrets appear in source code or documentation.
- [ ] Previously exposed tokens have been revoked, not merely deleted.
- [ ] Production secrets are stored in a secret manager.
- [ ] Telegram requests use HTTPS, timeouts, and response validation.
- [ ] Logs do not print tokens or complete request URLs containing tokens.
- [ ] Dependencies are updated and reviewed regularly.

## Contributing

Contributions are welcome. Please open an issue describing the proposed change before submitting a large pull request.

For code changes:

1. Create a feature branch.
2. Add or update tests.
3. Run the test and lint suites.
4. Keep secrets and generated files out of commits.
5. Submit a pull request with a clear description of the behavior change.

## License

Add the license you want to use—for example, the MIT License—in a `LICENSE` file, then update this section:

```text
This project is licensed under the MIT License. See LICENSE for details.
```

Until a license is added, normal copyright restrictions apply and others do not automatically have permission to copy, modify, or distribute the project.

## Disclaimer

This software is provided without warranty. It may miss signals, produce false signals, disconnect, or process incorrect timestamps or prices. You are solely responsible for validating its behavior and for any decisions made using its output.
