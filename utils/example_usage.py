#!/usr/bin/env python3
"""
Παράδειγμα χρήσης του Auto Backtesting System.

Δείχνει πώς να χρησιμοποιήσετε το system programmatically.
"""

import sys
import os

# Add user_data to path για imports
current_dir = os.path.dirname(os.path.abspath(__file__))
user_data_path = os.path.join(current_dir, "user_data")
sys.path.insert(0, user_data_path)

from auto_backtest import BacktestConfig, BacktestRunner


def basic_usage_example():
    """Βασικό παράδειγμα χρήσης."""
    print("=== Βασικό Παράδειγμα ===")

    # Δημιουργία configuration με default values
    config = BacktestConfig()

    # Εκτέλεση backtesting
    runner = BacktestRunner(config)
    success = runner.run()

    if success:
        print("✅ Backtesting completed successfully!")
    else:
        print("❌ Backtesting failed after all retries.")

    return success


def custom_configuration_example():
    """Παράδειγμα με custom configuration."""
    print("=== Custom Configuration Παράδειγμα ===")

    # Δημιουργία custom configuration
    config = BacktestConfig(
        strategy="MyCustomStrategy",
        timerange="20250101-20250131",
        max_retries=5,
        retry_wait=15,
        hang_timeout=600,  # 10 minutes
        exchange="kraken",
        timeframe="1h"
    )

    print(f"Strategy: {config.strategy}")
    print(f"Timerange: {config.timerange}")
    print(f"Max Retries: {config.max_retries}")
    print(f"Hang Timeout: {config.hang_timeout}s")
    print(f"Exchange: {config.exchange}")
    print("-" * 40)

    # Εκτέλεση backtesting
    runner = BacktestRunner(config)
    success = runner.run()

    return success


def multiple_strategies_example():
    """Παράδειγμα με πολλαπλές strategies."""
    print("=== Multiple Strategies Παράδειγμα ===")

    strategies = ["Strategy1", "Strategy2", "Strategy3"]
    results = {}

    for strategy in strategies:
        print(f"\n🔄 Testing strategy: {strategy}")

        config = BacktestConfig(
            strategy=strategy,
            timerange="20250102-20250109",
            max_retries=3,
            hang_timeout=300
        )

        runner = BacktestRunner(config)
        success = runner.run()
        results[strategy] = success

        if success:
            print(f"✅ {strategy} completed successfully")
        else:
            print(f"❌ {strategy} failed")

    # Print summary
    print("\n=== Results Summary ===")
    for strategy, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{strategy}: {status}")

    return results


def main():
    """Main function με παραδείγματα χρήσης."""
    print("Auto Backtesting System - Usage Examples")
    print("=" * 50)

    try:
        # Uncomment το παράδειγμα που θέλετε να τρέξετε

        # Βασική χρήση
        # basic_usage_example()

        # Custom configuration
        # custom_configuration_example()

        # Multiple strategies (προσοχή: μπορεί να πάρει πολλή ώρα)
        # multiple_strategies_example()

        print("\nΓια να τρέξετε κάποιο παράδειγμα, uncomment την αντίστοιχη γραμμή στο main().")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Examples interrupted by user.")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()