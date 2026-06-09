"""
Risk Management Module for Trading Bot
"""

import logging
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and position sizing"""

    def __init__(self, config=None):
        """
        Initialize Risk Manager
        
        Args:
            config: Configuration dictionary with risk parameters
        """
        self.config = config or {}
        
        # Risk parameters
        self.max_daily_loss = self.config.get('MAX_DAILY_LOSS', 100)
        self.max_concurrent_trades = self.config.get('MAX_CONCURRENT_TRADES', 3)
        self.min_stake = self.config.get('MIN_STAKE', 1)
        self.max_stake = self.config.get('MAX_STAKE', 50)
        self.kelly_fraction = self.config.get('KELLY_FRACTION', 0.25)
        self.stop_after_losses = self.config.get('STOP_AFTER_LOSSES', 5)
        self.adaptive_stake_sizing = self.config.get('ADAPTIVE_STAKE_SIZING', True)
        
        # Trading state
        self.daily_loss = 0
        self.daily_profit = 0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.open_trades = 0
        self.total_trades = 0
        self.win_rate = 0
        self.session_start_time = datetime.now()
        
        # Trade history
        self.trade_history = deque(maxlen=100)
        self.daily_trades = []
        
        logger.info(f"💰 Risk Manager initialized - Max daily loss: ${self.max_daily_loss}")

    def can_open_trade(self):
        """
        Check if a new trade can be opened based on risk parameters
        
        Returns:
            Tuple: (can_trade: bool, reason: str)
        """
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            return False, f"Daily loss limit exceeded (${self.daily_loss}/${self.max_daily_loss})"
        
        # Check concurrent trades
        if self.open_trades >= self.max_concurrent_trades:
            return False, f"Max concurrent trades reached ({self.open_trades}/{self.max_concurrent_trades})"
        
        # Check consecutive losses
        if self.consecutive_losses >= self.stop_after_losses:
            return False, f"Stop after {self.stop_after_losses} consecutive losses"
        
        return True, "OK"

    def calculate_stake(self, account_balance=100):
        """
        Calculate optimal stake using Kelly Criterion and adaptive sizing
        
        Args:
            account_balance: Current account balance
            
        Returns:
            Stake amount (float)
        """
        base_stake = self.config.get('STAKE', 10)
        
        if not self.adaptive_stake_sizing or self.total_trades < 10:
            return min(max(base_stake, self.min_stake), self.max_stake)
        
        # Kelly Criterion: f = (bp - q) / b
        if self.win_rate > 0:
            p = self.win_rate
            q = 1 - p
            kelly_fraction = (p - q) / 1
            kelly_fraction = max(0, kelly_fraction)
            kelly_fraction = min(kelly_fraction, 0.25)
            
            kelly_fraction = kelly_fraction * self.kelly_fraction
            
            stake = account_balance * kelly_fraction
        else:
            stake = base_stake
        
        stake = min(max(stake, self.min_stake), self.max_stake)
        
        logger.debug(f"Calculated stake: ${stake:.2f}")
        return stake

    def record_trade(self, trade_data):
        """
        Record a trade result
        
        Args:
            trade_data: Dict with 'result', 'stake', 'profit/loss', 'confidence'
        """
        result = trade_data.get('result')  # 'WIN', 'LOSS', 'DRAW'
        pnl = trade_data.get('pnl', 0)  # Profit/loss
        
        self.total_trades += 1
        self.trade_history.append(trade_data)
        self.daily_trades.append(trade_data)
        
        # Update PnL
        if result == 'WIN':
            self.daily_profit += pnl
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            logger.info(f"✅ Trade WIN - P&L: +${pnl:.2f}, Total: ${self.daily_profit:.2f}")
        elif result == 'LOSS':
            self.daily_loss += abs(pnl)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            logger.warning(f"❌ Trade LOSS - P&L: ${pnl:.2f}, Total Loss: ${self.daily_loss:.2f}")
        else:
            logger.info(f"⚪ Trade DRAW - P&L: ${pnl:.2f}")
        
        # Update win rate
        self.win_rate = self.get_win_rate()
        
        logger.info(f"Trades: {self.total_trades}, Win Rate: {self.win_rate:.2%}, "
                   f"Consecutive: {self.consecutive_wins if result == 'WIN' else self.consecutive_losses} "
                   f"({result})")

    def open_trade(self):
        """Increment open trades counter"""
        self.open_trades += 1
        logger.debug(f"Trade opened. Open trades: {self.open_trades}")

    def close_trade(self):
        """Decrement open trades counter"""
        if self.open_trades > 0:
            self.open_trades -= 1
        logger.debug(f"Trade closed. Open trades: {self.open_trades}")

    def get_win_rate(self):
        """
        Calculate win rate from trade history
        
        Returns:
            Win rate as percentage (0-1)
        """
        if len(self.trade_history) == 0:
            return 0
        
        wins = sum(1 for trade in self.trade_history if trade.get('result') == 'WIN')
        return wins / len(self.trade_history)

    def get_profit_factor(self):
        """
        Calculate profit factor (gross profit / gross loss)
        
        Returns:
            Profit factor (float)
        """
        gross_wins = sum(max(0, trade.get('pnl', 0)) for trade in self.trade_history)
        gross_losses = sum(max(0, -trade.get('pnl', 0)) for trade in self.trade_history)
        
        if gross_losses == 0:
            return float('inf') if gross_wins > 0 else 0
        
        return gross_wins / gross_losses

    def get_sharpe_ratio(self):
        """
        Calculate Sharpe Ratio (simplified)
        
        Returns:
            Sharpe ratio (float)
        """
        if len(self.trade_history) < 2:
            return 0
        
        returns = [trade.get('pnl', 0) for trade in self.trade_history]
        mean_return = sum(returns) / len(returns)
        
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        sharpe_ratio = mean_return / std_dev
        return sharpe_ratio

    def get_daily_reset_needed(self):
        """
        Check if daily stats need to be reset
        
        Returns:
            bool: True if new day started
        """
        return datetime.now().date() > self.session_start_time.date()

    def reset_daily_stats(self):
        """Reset daily statistics"""
        logger.info(f"Daily stats - Profit: ${self.daily_profit:.2f}, Loss: ${self.daily_loss:.2f}")
        self.daily_loss = 0
        self.daily_profit = 0
        self.daily_trades = []
        self.session_start_time = datetime.now()
        logger.info("Daily stats reset")

    def get_stats(self):
        """
        Get comprehensive trading statistics
        
        Returns:
            Dictionary with all stats
        """
        return {
            'total_trades': self.total_trades,
            'open_trades': self.open_trades,
            'win_rate': f"{self.win_rate:.2%}",
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses,
            'daily_profit': f"${self.daily_profit:.2f}",
            'daily_loss': f"${self.daily_loss:.2f}",
            'daily_net': f"${self.daily_profit - self.daily_loss:.2f}",
            'profit_factor': f"{self.get_profit_factor():.2f}",
            'sharpe_ratio': f"{self.get_sharpe_ratio():.2f}",
            'daily_loss_limit': f"${self.max_daily_loss:.2f}",
            'max_concurrent_trades': self.max_concurrent_trades,
        }
