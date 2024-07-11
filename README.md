# Resumes Parser Bot

Resumes Parser Bot is a Telegram bot that allows users to parse resumes from work.ua and robota.ua. Users can specify job position, location, and keywords to filter the resumes they are interested in.

## Features

- Choose between two job sites: work.ua and robota.ua.
- Set job position, location, and keywords to filter resumes.
- Fetch and display resumes based on specified criteria.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/paashkovaaa/resumes_parsing_project.git
    cd resumes_parsing_project
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your Telegram bot:

    - Create a new bot on Telegram and obtain the token. Follow the instructions from the [Telegram Bot Father](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

5. Create a `.env` file based on the `.env.sample` and add your bot token:

    ```env
    TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    ```

## Usage

1. Run the bot:

    ```bash
    python main.py
    ```

2. Start a conversation with your bot on Telegram.

3. Follow the prompts to select the job site, set the job position, location, and keywords.

4. Fetch and view resumes based on your criteria.

## Code Overview

The bot is implemented using the `python-telegram-bot` library. Below is a brief overview of the main components:

- `main.py`: The entry point of the application.
- `data/`: Contains data models and structures.
  - `resume.py`: Defines the structure of a resume.
- `parsers/`: Contains parsers for different job sites.
  - `robota_ua_parser.py`: Parser for fetching resumes from robota.ua.
  - `work_ua_parser.py`: Parser for fetching resumes from work.ua.
- `telegram_bot/`: Contains the bot's logic and handlers.
  - `telegram_bot.py`: Main bot script that handles the conversation flow and interactions with users.
- `utils/`: Contains utility functions.
  - `filters.py`: Functions for filtering and processing data.
