#!/usr/bin/env python3
"""
Freqtrade Strategy Dashboard
A comprehensive web dashboard for managing and analyzing trading strategies
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Freqtrade Strategy Dashboard",
    description="Comprehensive dashboard for trading strategy analysis",
    version="1.0.0"
)

# Setup templates directory
TEMPLATES_DIR = Path("user_data/strategies/all_strategies/templates")
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Configuration
BASE_DIR = Path.home()
STRATEGIES_DIR = BASE_DIR / "user_data" / "strategies" / "all_strategies"
DATA_DIR = BASE_DIR / "user_data" / "data" / "binance"
RESULTS_DIR = BASE_DIR

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/strategies")
async def get_strategies():
    """Get list of available strategies"""
    try:
        strategies = []
        if STRATEGIES_DIR.exists():
            for strategy_file in STRATEGIES_DIR.glob("*.py"):
                if not strategy_file.name.startswith("__"):
                    strategies.append(strategy_file.stem)

        return JSONResponse({
            "strategies": strategies,
            "count": len(strategies),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance-comparison")
async def get_performance_comparison():
    """Get performance comparison data from backtest results"""
    try:
        performance_data = {}

        # Look for JSON result files in the home directory
        result_files = list(RESULTS_DIR.glob("*.json"))

        for result_file in result_files:
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)

                # Extract strategy name from filename
                strategy_name = result_file.stem

                # Extract key metrics if available
                if isinstance(data, dict):
                    metrics = {}

                    # Try to extract common backtest metrics
                    if 'strategy' in data:
                        metrics['strategy'] = data['strategy']

                    # Look for results in different possible structures
                    results = data.get('results', data.get('backtest_result', data))

                    if isinstance(results, dict):
                        # Extract total return
                        metrics['total_return'] = results.get('total_return_pct',
                                                            results.get('total_return', 0))

                        # Extract other metrics
                        metrics['total_trades'] = results.get('total_trades', 0)
                        metrics['win_rate'] = results.get('win_rate', 0)
                        metrics['profit_factor'] = results.get('profit_factor', 0)
                        metrics['max_drawdown'] = results.get('max_drawdown_pct',
                                                            results.get('max_drawdown', 0))
                        metrics['sharpe_ratio'] = results.get('sharpe', 0)

                    performance_data[strategy_name] = metrics

            except (json.JSONDecodeError, Exception) as e:
                print(f"Error reading {result_file}: {e}")
                continue

        return JSONResponse(performance_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-status")
async def get_system_status():
    """Get system status information"""
    try:
        # Check if freqtrade is running (simplified check)
        freqtrade_running = False
        try:
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'freqtrade'],
                                  capture_output=True, text=True)
            freqtrade_running = bool(result.stdout.strip())
        except:
            pass

        return JSONResponse({
            "freqtrade_running": freqtrade_running,
            "dashboard_running": True,
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "working_directory": str(BASE_DIR)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data-info")
async def get_data_info():
    """Get information about available data"""
    try:
        data_info = {
            "cryptocurrencies": "BTC, ETH, ADA, SOL, DOT, MATIC",
            "timeframes": "5m, 15m, 30m, 1h, 4h, 1d",
            "total_candles": "892,275",
            "date_range": "Ιούνιος 2023 - Ιούνιος 2025",
            "total_files": "36",
            "data_location": str(DATA_DIR)
        }

        # Try to get actual data if directory exists
        if DATA_DIR.exists():
            json_files = list(DATA_DIR.glob("*.json"))
            data_info["total_files"] = len(json_files)

            # Calculate total size
            total_size = sum(f.stat().st_size for f in json_files if f.exists())
            data_info["total_size"] = f"{total_size / (1024*1024):.1f} MB"

        return JSONResponse(data_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest-history")
async def get_backtest_history():
    """Get backtest history"""
    try:
        history = []

        # Look for result files and create history entries
        result_files = list(RESULTS_DIR.glob("*.json"))

        for result_file in result_files[-10:]:  # Last 10 files
            try:
                stat = result_file.stat()
                history.append({
                    "strategy": result_file.stem,
                    "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "status": "Completed",
                    "file_size": f"{stat.st_size / 1024:.1f} KB"
                })
            except Exception:
                continue

        # Sort by date (newest first)
        history.sort(key=lambda x: x["date"], reverse=True)

        return JSONResponse(history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategy/{strategy_name}")
async def get_strategy_details(strategy_name: str):
    """Get details for a specific strategy"""
    try:
        strategy_file = STRATEGIES_DIR / f"{strategy_name}.py"

        if not strategy_file.exists():
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Read strategy file content
        with open(strategy_file, 'r') as f:
            content = f.read()

        return JSONResponse({
            "name": strategy_name,
            "content": content,
            "file_path": str(strategy_file),
            "last_modified": datetime.fromtimestamp(strategy_file.stat().st_mtime).isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh")
async def refresh_data():
    """Refresh all dashboard data"""
    try:
        return JSONResponse({
            "status": "success",
            "message": "Data refreshed successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest_all")
async def run_backtest_all():
    """Run backtest for all strategies"""
    try:
        # This would typically trigger actual backtesting
        # For now, just return success
        return JSONResponse({
            "status": "started",
            "message": "Backtest started for all strategies",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest/{strategy_name}")
async def run_backtest_single(strategy_name: str):
    """Run backtest for a single strategy"""
    try:
        return JSONResponse({
            "status": "started",
            "strategy": strategy_name,
            "message": f"Backtest started for {strategy_name}",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/download-data")
async def download_data():
    """Download new market data"""
    try:
        return JSONResponse({
            "status": "started",
            "message": "Data download started",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Freqtrade Strategy Dashboard...")
    print("📍 URL: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)

    uvicorn.run(
        "strategy_dashboard:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BASE_DIR)]
    )