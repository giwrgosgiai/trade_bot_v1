# ==============================================================================================
# Made by:
# ______         _         _      _____                      _         ______            _
# |  _  \       | |       | |    /  __ \                    | |        |  _  \          | |
# | | | | _   _ | |_  ___ | |__  | /  \/ _ __  _   _  _ __  | |_  ___  | | | | __ _   __| |
# | | | || | | || __|/ __|| '_ \ | |    | '__|| | | || '_ \ | __|/ _ \ | | | |/ _` | / _` |
# | |/ / | |_| || |_| (__ | | | || \__/\| |   | |_| || |_) || |_| (_) || |/ /| (_| || (_| |
# |___/   \__,_| \__|\___||_| |_| \____/|_|    \__, || .__/  \__|\___/ |___/  \__,_| \__,_|
#                                               __/ || |
#                                              |___/ |_|
#
# ==============================================================================================
# 📙 MY BOOK FOR BEGINNING ALGORITHMIC TRADING: Algorithmic Cryptocurrency Trading For Beginners : bit.ly/DCD_Ebook1
# 💰 Patreon community: https://www.patreon.com/dutchalgotrading
# ☕️ For a One-time support donation, click here : https://ko-fi.com/dutchcryptodad
# 🌐 website: http://www.dutchalgotrading.com#
# ==============================================================================================
# Some helpful commands:
# freqtrade backtesting -s <STRATEGY_NAME> -c user_data/spot_config.json --timeframe=5m --timerange=20210101-20210601
# freqtrade backtesting -s <STRATEGY_NAME> -p BTC/USDT -c user_data/spot_config.json --timeframe=5m
# freqtrade plot-dataframe -s <STRATEGY_NAME> -p BTC/USDT -c user_data/spot_config.json --timeframe=5m
# freqtrade hyperopt -c user_data/spot_config.json -s <STRATEGY_NAME> --epochs 50 --spaces buy --hyperopt-loss SharpeHyperOptLoss
# freqtrade hyperopt -s <STRATEGY_NAME> -c user_data/spot_config.json --timeframe=5m --timerange=20210101-20210601 --hyperopt-loss
# ShortTradeDurHyperOptLoss --epochs 10 --spaces roi stoploss --job-workers 2
# freqtrade trade -s <STRATEGY_NAME> -c user_data/spot_config.json
# ==============================================================================================
# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Union

from freqtrade.strategy import (
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    IStrategy,
    merge_informative_pair,
    # stoploss_from_absolute is imported inside custom_stoploss to avoid loading when not needed
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import bamboo_ta as bta
from technical import qtpylib
# logging and os are imported conditionally based on use_custom_stoploss

from freqtrade.persistence import Trade

# logger is initialized conditionally based on use_custom_stoploss


class NeverMissATrend(IStrategy):
    """
    This strategy uses linear regression to determine the trend of the price.
    Integrated with the trade_bot_v1 system alongside NFI5MOHO.
    """

    def __init__(self, config: dict, *args, **kwargs):  # Accept config explicitly
        # Pass config to the base class
        super().__init__(config, *args, **kwargs)

        # Initialize trade_log_file and logger only if custom_stoploss is enabled
        self.trade_log_file = None
        self.logger = None

        if getattr(self, "use_custom_stoploss", False):
            import logging
            import os

            self.logger = logging.getLogger(__name__)

            # Set up a specific file for trade logs
            self.trade_log_file = os.path.join(
                os.getcwd(), f"trades_log_{self.__class__.__name__}_{self.timeframe}.log"
            )  # Log file uses class name and timeframe dynamically

            # Ensure the file exists or create it
            if not os.path.exists(self.trade_log_file):
                with open(self.trade_log_file, "w") as f:
                    f.write("Trade Log\n")  # Header for the log file

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = "1d"

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {"0": 100.00}

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -1

    # Trailing stoploss
    trailing_stop = False

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_custom_stoploss = False
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 50

    # Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate indicators for the NeverMissATrend strategy.
        Uses linear regression slope and center of gravity indicators.
        """
        # Exponential Moving Average
        dataframe["ema"] = bta.exponential_moving_average(dataframe, "close", 50)

        # Linear Regression
        lrs = bta.linear_regression_slope(
            dataframe, curve_length=21, slope_length=10, signal_length=7
        )
        dataframe["lrs"] = lrs["lrs"]  # Raw Linear Regression Slope
        dataframe["slrs"] = lrs["slrs"]  # Smoothed Linear Regression Slope (main indicator)
        dataframe["alrs"] = lrs["alrs"]  # Signal line
        dataframe["trend"] = lrs[
            "trend"
        ]  # Trend indicator (1: accelerating up, -1: accelerating down, 0: neutral)

        # center of gravity
        cg_df = bta.center_of_gravity(dataframe, length=10)
        dataframe["cg"] = cg_df["cg"]
        dataframe["cg_prev"] = cg_df["cg_prev"]

        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ("live", "dry_run"):
                ob = self.dp.orderbook(metadata["pair"], 1)
                dataframe["best_bid"] = ob["bids"][0][0]
                dataframe["best_ask"] = ob["asks"][0][0]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate entry signals based on linear regression slope and center of gravity.
        """
        # Decide which trading rule should be used
        use_lrs = True

        # LONG Entry condition 1
        if use_lrs:
            dataframe.loc[
                (
                    # Enter long if the close price is above the EMA
                    (dataframe["close"] > dataframe["ema"])
                    &
                    # and when smoothed linear regression slope is above 0
                    (dataframe["slrs"] > 0)
                    &
                    # and when center of gravity is above the previous center of gravity
                    (dataframe["cg"] > dataframe["cg_prev"])
                ),
                ["enter_long", "enter_tag"],
            ] = (
                1,
                "upward_trend",
            )

            if self.can_short:
                dataframe.loc[
                    (
                        # Enter short if the close price is below the EMA
                        (dataframe["close"] < dataframe["ema"])
                        &
                        # and when smoothed linear regression slope is below 0
                        (dataframe["slrs"] < 0)
                        &
                        # and when center of gravity is below the previous center of gravity
                        (dataframe["cg"] < dataframe["cg_prev"])
                    ),
                    ["enter_short", "enter_tag"],
                ] = (
                    1,
                    "downward_trend",
                )

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate exit signals based on linear regression slope crossovers.
        """
        use_lrs_exit = True
        use_cg_exit = False

        if use_lrs_exit:
            # When long, exit when smoothed linear regression slope is below the signal line
            dataframe.loc[
                # Check if this is a long position
                (dataframe["slrs"] < dataframe["alrs"]),
                ["exit_long", "exit_tag"],
            ] = (1, "lrs_long_exit")

            # When short, exit when smoothed linear regression slope is above the signal line
            if self.can_short:
                dataframe.loc[
                    (dataframe["slrs"] > dataframe["alrs"]),
                    ["exit_short", "exit_tag"],
                ] = (1, "lrs_short_exit")

        if use_cg_exit:
            # When long, exit when center of gravity is below the previous center of gravity
            dataframe.loc[
                (dataframe["cg"] < dataframe["cg_prev"]),
                ["exit_long", "exit_tag"],
            ] = (1, "cg_long_exit")

            # When short, exit when center of gravity is above the previous center of gravity
            if self.can_short:
                dataframe.loc[
                    (dataframe["cg"] > dataframe["cg_prev"]),
                    ["exit_short", "exit_tag"],
                ] = (1, "cg_short_exit")
        return dataframe

    lookback_period = 5  # Number of candles to look back for swing low/high
    risk_reward_ratio = 1.5  # Risk:Reward ratio for take profit calculation

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> float | None:
        """
        Custom stoploss that uses:
        - For longs: lowest low over lookback period as permanent stop loss
        - For shorts: highest high over lookback period as permanent stop loss
        - Sets take profit target at risk:reward ratio from entry
        """
        # Import stoploss_from_absolute here to avoid loading it when not needed
        from freqtrade.strategy import stoploss_from_absolute

        # Get the analyzed dataframe for this pair
        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)

        # Get candles for lookback period
        lookback_candles = dataframe.tail(self.lookback_period)

        # Calculate stop loss level
        if trade.is_short and self.can_short:
            # For shorts, use the highest high
            stop_price = lookback_candles["high"].max()
        else:
            # For longs, use the lowest low
            stop_price = lookback_candles["low"].min()

        # Calculate take profit target based on risk:reward ratio
        risk_amount = abs(trade.open_rate - stop_price)
        reward_amount = risk_amount * self.risk_reward_ratio

        if trade.is_short:
            take_profit = trade.open_rate - reward_amount
        else:
            take_profit = trade.open_rate + reward_amount

        # Convert stop price to percentage
        stoploss_percent = stoploss_from_absolute(stop_price, current_rate, is_short=trade.is_short)

        # Log stop loss and take profit levels if logger is initialized
        if self.logger and self.trade_log_file:
            log_message = (
                f"Trade Settings: Pair={pair}, "
                f"EntryPrice={trade.open_rate:.2f}, StopPrice={stop_price:.2f}, "
                f"TakeProfit={take_profit:.2f}, Type={'Short' if trade.is_short else 'Long'}, "
                f"Time={current_time}"
            )
            self.logger.info(log_message)
            with open(self.trade_log_file, "a") as file:
                file.write(log_message + "\n")

        return -stoploss_percent