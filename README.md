# Solana Wallet Telegram Bot 🤖💸

## Overview

A powerful Telegram bot for seamless Solana wallet management. Empowering users to interact with their cryptocurrency wallets directly through Telegram, with features including:

- 📝 User Registration
- 🌐 Network Switching
- 💰 Balance Checking
- 💸 SOL Token Transfers

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Handlers](#handlers)
- [Running the Bot](#running-the-bot)
- [License](#license)

## Installation 🛠️

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd bot-code
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv .venv
    ```

3. **Activate the virtual environment:**
    - On Windows:
        ```sh
        .venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source .venv/bin/activate
        ```

4. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Configuration 🔧

Create a `.env` file in the `bot-code` directory with the following variables:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
API_BASE_URL=your_backend_api_base_url
API_TOKEN=your_api_token
```

## Commands �令

### `/start`
- **Description:** Start the bot and display a welcome message with available commands
- **Handler:** `start_command`

### `/signup`
- **Description:** Register a new Solana wallet
- **Handler:** `signup_command`
- **Conversation States:**
  - `SIGNUP_PASSWORD`: Collect the user's password
  - `WALLET_NAME`: Collect the wallet name

### `/switchnetwork`
- **Description:** Switch to mainnet, devnet, or connect to Solana blockchain using a custom RPC URL
- **Handler:** `switchnetwork_command`
- **Conversation States:**
  - `SIGNUP_PASSWORD`: Collect the user's password
  - `NETWORK_SELECTION`: Collect the network selection
  - `CUSTOM_RPC_URL`: Collect the custom RPC URL

### `/balance`
- **Description:** Check the native SOL balance of a wallet
- **Handler:** `balance_command`
- **Conversation States:**
  - `SIGNUP_PASSWORD`: Collect the user's password
  - `BALANCE`: Collect the wallet name and display the balance

### `/transfer`
- **Description:** Transfer SOL to another wallet
- **Handler:** `transfer_command`
- **Conversation States:**
  - `TRANSFER_RECEIVER`: Collect the receiver's wallet address
  - `TRANSFER_AMOUNT`: Collect the amount of SOL to transfer
  - `SIGNUP_PASSWORD`: Collect the user's password
  - `TRANSFER_WALLET`: Collect the wallet name and complete the transfer

## Handlers 🎮

### `start_command`
- **Description:** Handles the `/start` command and sets the bot commands

### `signup_command`
- **Description:** Initiates the signup process and collects the user's password and wallet name

### `switchnetwork_command`
- **Description:** Initiates the network switching process and collects the user's password and network selection

### `balance_command`
- **Description:** Initiates the balance check process and collects the user's password and wallet name

### `transfer_command`
- **Description:** Initiates the SOL transfer process and collects the receiver's wallet address, amount, password, and wallet name

## Running the Bot 🚀

1. **Activate the virtual environment:**
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```

2. **Start the bot:**
   ```sh
   python bot.py
   ```

## License 📄

This project is licensed under the MIT License.

## Technologies 🖥️

![Python](https://img.shields.io/badge/Python-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-blue?logo=telegram)
![Solana](https://img.shields.io/badge/Solana-purple?logo=solana)

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.