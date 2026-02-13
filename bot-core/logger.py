"""
Simple trade logger for bot-core.
"""

import csv
import os
from datetime import datetime
from typing import Dict, Any, Optional

from config import LOG_FILE


def log_trade(trade: Dict[str, Any], log_file: Optional[str] = None) -> None:
    """Append a trade record to CSV.

    Args:
        trade: Dict with trade data.
        log_file: Optional override of CSV path.
    """
    file_path = log_file or LOG_FILE
    if not trade:
        return

    # Ensure timestamp exists
    trade = dict(trade)
    trade.setdefault("timestamp", datetime.now().isoformat())

    file_exists = os.path.exists(file_path)
    fieldnames = list(trade.keys())

    with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade)
