"""
Example Configuration File for Deriv Match Predictor
Copy this file to config.py and fill in your credentials
"""

# Deriv API Configuration
DERIV_API_KEY = "your_api_key_here"
DERIV_USER_ID = "your_user_id_here"
DERIV_APP_ID = "your_app_id_here"

# Trading Symbols
SYMBOLS = [
    'EURUSD',
    'GBPUSD',
    'USDJPY',
    'AUDUSD',
]

# Risk Management Parameters
MAX_DAILY_LOSS = 100  # Stop trading after this daily loss ($)
MAX_CONCURRENT_TRADES = 3  # Maximum open trades at once
MIN_STAKE = 1  # Minimum stake amount ($)
MAX_STAKE = 50  # Maximum stake amount ($)
KELLY_FRACTION = 0.25  # Kelly Criterion fraction (0-1, lower = more conservative)
STOP_AFTER_LOSSES = 5  # Stop trading after N consecutive losses
ADAPTIVE_STAKE_SIZING = True  # Enable adaptive stake sizing based on win rate
STAKE = 10  # Default stake amount ($)

# Market Analysis Parameters
TIMEFRAME = '5m'  # Timeframe for analysis (1m, 5m, 15m, 1h, etc.)
CANDLES_LOOKBACK = 100  # Number of candles to analyze
MIN_CONFIDENCE = 0.75  # Minimum confidence threshold for trades

# Prediction Model Parameters
USE_MACHINE_LEARNING = False  # Enable ML predictions
MODEL_PATH = 'models/prediction_model.pkl'  # Path to trained model

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'trading_bot.log'

# Advanced Settings
RETRY_ATTEMPTS = 3  # API retry attempts
RETRY_DELAY = 5  # Delay between retries (seconds)
REQUEST_TIMEOUT = 30  # Request timeout (seconds)
