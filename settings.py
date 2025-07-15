import os
import logging
import logfire
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configure Logfire: send only if token is present
logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_system_metrics()

# Set up logging with dynamic level
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("financial_analyzer.log"),
        logfire.LogfireLoggingHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Logging initialized with level {LOG_LEVEL}")

# Read keys from settings
FMP_API = os.getenv("FMP_API")

# Symbols to analyze
symbols = ["GOOG", "MSFT", "AMZN", "AAPL", "TSLA", "META", "NFLX", "NVDA", "ADBE", "INTC"]
sp500_tickers = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "AMZN",  # Amazon
    "GOOGL",  # Alphabet Class A
    "GOOG",  # Alphabet Class C
    "META",  # Meta Platforms (Facebook)
    "TSLA",  # Tesla
    "NVDA",  # Nvidia
    "BRK.B",  # Berkshire Hathaway Class B
    "JPM",  # JPMorgan Chase
    "JNJ",  # Johnson & Johnson
    "XOM",  # Exxon Mobil
    "PG",  # Procter & Gamble
    "UNH",  # UnitedHealth Group
    "HD",  # Home Depot
    "V",  # Visa
    "MA",  # Mastercard
    "BAC",  # Bank of America
    "DIS",  # Walt Disney
    "KO"  # Coca-Cola
]

email_address = os.getenv("EMAIL_ADDRESS")
