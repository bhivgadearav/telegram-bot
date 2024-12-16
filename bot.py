import os
import logging
import requests
import telegram
from telegram.ext import (
    Updater, CommandHandler, ConversationHandler, 
    MessageHandler, filters as Filters, Application
)
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

default_keys = [
    {
        'name': 'Help',
        'command': 'help'
    },
    {
        'name': 'Balance',
        'command': 'balance'
    },
    {
        'name': 'Transfer',
        'command': 'transfer'
    },
    {
        'name': 'Switch Network',
        'command': 'switchnetwork'
    },
    {
        'name': 'Transfer',
        'command': 'transfer'
    }
]

commands = [
    {"command": "help", "description": "Get a list of available commands with their use"},
    {"command": "signup", "description": "Register with your telegram account."},
    {"command": "balance", "description": "Check wallet balance"},
    {"command": "transfer", "description": "Transfer SOL to another wallet"},
    {"command": "switchnetwork", "description": "Switch Solana networks"},
]

class SolanaWalletTelegramBot:
    def __init__(self, bot_token, server_url):
        """
        Initialize Telegram Solana Wallet Bot
        
        Args:
            bot_token (str): Telegram Bot API token
            server_url (str): Backend server base URL
        """
        # Logging setup
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        
        # Bot configuration
        self.bot_token = bot_token
        self.server_url = server_url
        
        # Conversation states
        (
            self.SIGNUP_PASSWORD,
            self.NETWORK_SELECTION,
            self.CUSTOM_RPC_URL,
            self.WALLET_NAME,
            self.BALANCE,
            self.TRANSFER_RECEIVER,
            self.TRANSFER_AMOUNT,
            self.TRANSFER_WALLET
        ) = range(8)

    def get_default_reply_markup(self, commands):
        """
        Get command keys
        """
        keyboard = [
            [telegram.InlineKeyboardButton(key['name'], callback_data=key['command'])]
            for key in default_keys
        ]

        default_reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        return default_reply_markup
            

    def extract_telegram_user_info(self, update):
        """
        Extract comprehensive user information from Telegram
        
        Returns:
            dict: Detailed user identification information
        """
        user = update.effective_user
        return {
            'telegramId': str(user.id),
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code
        }

    async def handle_server_error(self, update, error_response):
        """
        Standardized error handling for server responses
        
        Args:
            update (Update): Telegram update object
            error_response (dict): Error response from server
        """
        # Extract error details
        error = error_response.get('error', 'Unknown Error')
        details = error_response.get('details', '')
        
        # Construct user-friendly error message
        error_message = f"❌ {error}"
        if details:
            error_message += f"\n📝 Details: {details}"
        
        # Send error to user
        await update.message.reply_text(error_message)
    
    async def set_commands(self, update):
        response = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/setMyCommands",
            json={"commands": commands}
        )
        if response.status_code != 200:
            await self.handle_server_error(update, response.json())

    async def start_command(self, update, context): 
        """
        Start command handler
        """
        await self.set_commands(update) # Set commands
        default_reply_markup = self.get_default_reply_markup(default_keys)
        await update.message.reply_text(
            "🚀 Welcome to Solana Wallet Bot!\n"
            "Use /signup to create a new wallet.\n"
            "Use /balance to check your wallet balance.\n"
            "Use /transfer to send SOL to another wallet.\n"
            "Use /switchnetwork to switch Solana networks.\n"
            "Available networks: mainnet-beta, testnet, devnet, custom.\n"
            "You can use custom network to connect to solana using your own RPC url.\n"
            "Use /help to see this message again.",
            reply_markup=default_reply_markup
        )

    async def signup_command(self, update, context):
        """
        Initiate signup process
        """
        await update.message.reply_text(
            "🚀 Welcome to Solana Wallet Signup!\n"
            "Please enter a secure password to create your wallet:"
        )
        return self.SIGNUP_PASSWORD

    async def password_handler(self, update, context):
        """
        Collect the user's password.
        """
        password = update.message.text
        if not password:
            await update.message.reply_text("Password cannot be empty. Please enter a valid password:")
            return self.SIGNUP_PASSWORD

        context.user_data['password'] = password  # Store the password
        await update.message.reply_text("Great! Now, please enter a name for your wallet:")
        return self.WALLET_NAME

    async def wallet_name_handler(self, update, context):
        """
        Collect the wallet name and finalize signup.
        """
        wallet_name = update.message.text
        if not wallet_name:
            await update.message.reply_text("Wallet name cannot be empty. Please enter a valid name:")
            return self.WALLET_NAME

        # Store the wallet name
        context.user_data['wallet_name'] = wallet_name

        # Proceed with signup
        await self.process_signup(update, context)
        return ConversationHandler.END


    async def process_signup(self, update, context):
        """
        Complete wallet creation process
        """
        password = context.user_data.get('password')
        wallet_name = context.user_data.get('wallet_name')

        # Validate inputs
        if not password or not wallet_name:
            await update.message.reply_text("Error: Missing password or wallet name. Please restart with /signup.")
            return ConversationHandler.END

        
        # Prepare signup payload
        signup_payload = {
            **self.extract_telegram_user_info(update),
            'name': wallet_name,
            'password': password
        }
        
        try:
            # Send signup request to backend
            response = requests.post(
                f"{self.server_url}/api/signup", 
                json=signup_payload
            )
            
            if response.status_code == 201:
                # Successful signup
                wallet_data = response.json()
                
                # Securely send wallet details
                await update.message.reply_text(
                    "🎉 Wallet created successfully!\n\n"
                    "🔑 Your wallet details have been generated securely. "
                    "Please keep your mnemonic and private key safe.\n\n"
                    f"🔐 Public Key: {wallet_data.get('publicKey')}"
                )
                
                # Optionally, send mnemonic via private message
                # Check if it works
                # context.bot.send_message(
                #     chat_id=update.effective_user.id,
                #     text=f"🔐 Mnemonic (KEEP SECRET): {wallet_data.mnemonic}"
                #          f"\n🔑 Private Key (KEEP SECRET): {wallet_data.privateKey}"
                #          f"\n🔑 Public Key (YOU CAN SHARE THIS WITH ANYONE SO THEY CAN SEND YOU SOL/TOKENS): {wallet_data.publicKey}"
                #          f"\n\n🚨 Do not share this information with anyone!"
                # )
            else:
                # Handle signup errors
                await self.handle_server_error(update, response.json())
        
        except requests.RequestException as e:
            self.logger.error(f"Signup error: {e}")
            await update.message.reply_text(
                "🔴 Network error. Please try again later."
            )
        
        return ConversationHandler.END

    async def switchnetwork_command(self, update, context):
        """
        Network switching interface
        """
        # Predefined network options
        networks = [
            'mainnet-beta', 
            'testnet', 
            'devnet', 
            'custom'
        ]
        
        # Create keyboard markup
        keyboard = [
            [telegram.KeyboardButton(network)] 
            for network in networks
        ]
        reply_markup = telegram.ReplyKeyboardMarkup(
            keyboard, 
            one_time_keyboard=True
        )
        
        await update.message.reply_text(
            "🌐 Select a Solana network:",
            reply_markup=reply_markup
        )
        
        return self.SIGNUP_PASSWORD  # Reuse password collection state
    
    async def process_password_for_network_switch(self, update, context):
        """
        Collect password for network switch
        """
        network = update.message.text

        valid_networks = ['mainnet-beta', 'testnet', 'devnet', 'custom']

        # Validate the network selection
        if network not in valid_networks:
            await update.message.reply_text(
                "❌ Invalid network selected. Please choose from the available options:"
            )
            return self.NETWORK_SELECTION  # Repeat the selection step

        # Store the selected network in user_data
        context.user_data['network'] = network

        await update.message.reply_text(
            "🔑 Enter your password to switch networks:"
        )

        return self.NETWORK_SELECTION

    async def process_network_switch(self, update, context):
        """
        Handle network switching logic
        """
        password = update.message.text
        network = context.user_data.get('network', 'mainnet-beta') 
        
        # Check if custom network selected
        if network == 'custom':
            await update.message.reply_text(
                "🔗 Enter your custom RPC URL:"
            )
            return self.CUSTOM_RPC_URL
        
        # Prepare network switch payload
        switch_payload = {
            'telegramId': str(update.effective_user.id),
            'password': context.user_data.get('password', ''),
            'network': network,
            'password': password
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/network/switch", 
                json=switch_payload
            )
            
            if response.status_code == 200:
                await update.message.reply_text(
                    f"✅ Switched to {network} network successfully!"
                )
            else:
                await self.handle_server_error(update, response.json())
        
        except requests.RequestException as e:
            self.logger.error(f"Network switch error: {e}")
            await update.message.reply_text(
                "🔴 Network error. Please try again later."
            )
        
        return ConversationHandler.END

    async def process_custom_network(self, update, context):
        """
        Handle custom RPC URL network switch
        """
        custom_rpc_url = update.message.text
        password = context.user_data.get('password', '')
        
        # Prepare custom network payload
        switch_payload = {
            'telegramId': str(update.effective_user.id),
            'password': context.user_data.get('password', ''),
            'network': 'custom',
            'rpcUrl': custom_rpc_url,
            'password': password
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/network/switch", 
                json=switch_payload
            )
            
            if response.status_code == 200:
                await update.message.reply_text(
                    "✅ Custom network switched successfully!"
                )
            else:
                await self.handle_server_error(update, response.json())
        
        except requests.RequestException as e:
            self.logger.error(f"Custom network switch error: {e}")
            await update.message.reply_text(
                "🔴 Network error. Please try again later."
            )
        
        return ConversationHandler.END

    async def balance_command(self, update, context):
        """
        Initiate balance check process
        """
        await update.message.reply_text(
            "🏦 Enter the wallet index to check balance:"
        )
        return self.SIGNUP_PASSWORD  # Reuse password collection state
    
    async def process_password_for_balance(self, update, context):
        """
        Collect password for network switch
        """
        index = update.message.text
        context.user_data['wallet_index'] = index

        await update.message.reply_text(
            "🔑 Enter your password to switch networks:"
        )

        return self.BALANCE

    async def process_balance(self, update, context):
        """
        Retrieve and display wallet balance
        """
        password = update.message.text
        wallet_index = context.user_data.get('wallet_index', 0)
        
        # Prepare balance check payload
        balance_payload = {
            'telegramId': str(update.effective_user.id),
            'password': password,
            'walletIndex': wallet_index # Default to first wallet
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/balance", 
                json=balance_payload
            )
            
            if response.status_code == 200:
                balance_data = response.json()
                await update.message.reply_text(
                    f"💰 Balance: {balance_data['balance']} SOL"
                )
            else:
                await self.handle_server_error(update, response.json())
        
        except requests.RequestException as e:
            self.logger.error(f"Balance retrieval error: {e}")
            await update.message.reply_text(
                "🔴 Network error. Please try again later."
            )
        
        return ConversationHandler.END

    async def transfer_command(self, update, context):
        """
        Initiate SOL transfer process
        """
        await update.message.reply_text(
            "💸 Enter receiver's wallet address:"
        )
        return self.TRANSFER_RECEIVER

    async def process_transfer_receiver(self, update, context):
        """
        Collect receiver's wallet address
        """
        context.user_data['receiver_address'] = update.message.text
        
        await update.message.reply_text(
            "💰 Enter amount of SOL to transfer:"
        )
        
        return self.TRANSFER_AMOUNT

    async def process_transfer_amount(self, update, context):
        """
        Collect transfer amount
        """
        try:
            amount = float(update.message.text)
            context.user_data['transfer_amount'] = amount
            
            await update.message.reply_text(
                "🏦 Enter source wallet index:"
            )
            
            return self.TRANSFER_WALLET
        
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount. Please enter a valid number."
            )
            return self.TRANSFER_AMOUNT

    async def complete_transfer(self, update, context):
        """
        Execute SOL transfer
        """
        password = update.message.text
        
        # Prepare transfer payload
        transfer_payload = {
            'telegramId': str(update.effective_user.id),
            'password': password,
            'receiverAddress': context.user_data['receiver_address'],
            'amount': context.user_data['transfer_amount'],
            'walletIndex': 0  # Default to first wallet
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/transfer", 
                json=transfer_payload
            )
            
            if response.status_code == 200:
                transfer_data = response.json()
                await update.message.reply_text(
                    f"✅ Transfer successful!\n"
                    f"Transaction Signature: {transfer_data['signature']}"
                )
            else:
                await self.handle_server_error(update, response.json())
        
        except requests.RequestException as e:
            self.logger.error(f"Transfer error: {e}")
            await update.message.reply_text(
                "🔴 Network error. Please try again later."
            )
        
        return ConversationHandler.END

    def setup_handlers(self, dispatcher):
        """
        Configure conversation handlers for bot commands
        """

        # Start command handler
        start_handler = CommandHandler('start', self.start_command)
        dispatcher.add_handler(start_handler)

        # Help command handler
        help_handler = CommandHandler('help', self.start_command)
        dispatcher.add_handler(help_handler)

        # Signup conversation handler
        signup_handler = ConversationHandler(
            entry_points=[CommandHandler('signup', self.signup_command)],
            states={
                self.SIGNUP_PASSWORD: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.password_handler)
                ],
                self.WALLET_NAME: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.wallet_name_handler)
                ],
            },
            fallbacks=[],
        )

        # Network switch conversation handler
        network_switch_handler = ConversationHandler(
            entry_points=[CommandHandler('switchnetwork', self.switchnetwork_command)],
            states={
                self.SIGNUP_PASSWORD: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_password_for_network_switch)
                ],
                self.NETWORK_SELECTION: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_network_switch)
                ],
                self.CUSTOM_RPC_URL: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_custom_network)
                ]
            },
            fallbacks=[]
        )

        # Balance check conversation handler
        balance_handler = ConversationHandler(
            entry_points=[CommandHandler('balance', self.balance_command)],
            states={
                self.SIGNUP_PASSWORD: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_password_for_balance)
                ],
                self.BALANCE: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_balance)
                ]
            },
            fallbacks=[]
        )

        # Transfer conversation handler
        transfer_handler = ConversationHandler(
            entry_points=[CommandHandler('transfer', self.transfer_command)],
            states={
                self.TRANSFER_RECEIVER: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_transfer_receiver)
                ],
                self.TRANSFER_AMOUNT: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.process_transfer_amount)
                ],
                self.TRANSFER_WALLET: [
                    MessageHandler(Filters.TEXT & ~Filters.COMMAND, self.complete_transfer)
                ]
            },
            fallbacks=[]
        )

        # Add handlers to dispatcher
        dispatcher.add_handler(signup_handler)
        dispatcher.add_handler(network_switch_handler)
        dispatcher.add_handler(balance_handler)
        dispatcher.add_handler(transfer_handler)

def main():
    """
    Main bot setup and execution
    """
    # Initialize bot
    bot = SolanaWalletTelegramBot(
        bot_token=TELEGRAM_TOKEN,
        server_url=API_BASE_URL
    )
    
    # Create the application
    application = Application.builder().token(bot.bot_token).build()

    # Setup conversation handlers
    bot.setup_handlers(application)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()