# Telegram Username Occupier

A Python script to check the availability of Telegram usernames on [Fragment](https://fragment.com) and automatically occupy them using a Telegram session.

## Features

- Reads usernames from `resources/input_usernames.txt`.
- Checks if usernames are available on Fragment.
- Automatically occupies available usernames if configured.

## Prerequisites

- [Python 3.11+](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd telegram_username_occupier
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

## Configuration

1. **Setup environment variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```

2. **Configure `.env`:**
   - `API_ID` & `API_HASH`: Your Telegram API credentials (get them from [my.telegram.org](https://my.telegram.org)).
   - `SESSION_FILE_PATH`: Path to your `.session` file.
   - `TRY_TO_OCCUPY`: Set to `true` if you want the script to attempt to occupy free usernames.

## Usage

1. **Prepare your usernames:**
   Add the usernames you want to check to `resources/input_usernames.txt` (one per line).

2. **Run the script:**
   ```bash
   poetry run python main.py
   ```

## How it Works

The script iterates through each username in `resources/input_usernames.txt`:
1. It checks Fragment to see if the username is available (not sold, not active).
2. If a username is found to be free:
   - If `TRY_TO_OCCUPY` is set to `true` in your `.env`, it uses your Telegram session to attempt to claim the username.
   - Otherwise, it simply logs the availability.
