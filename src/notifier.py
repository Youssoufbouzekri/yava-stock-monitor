from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from src.config import Config

logger = logging.getLogger(__name__)


def send_telegram_notification(
    config: Config, product_title: str, flavor: str, product_url: str
) -> bool:
    if not config.telegram_bot_token or not config.telegram_chat_id:
        logger.warning(
            "Telegram credentials not configured. Skipping notification."
        )
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    message = (
        "\U0001f7e2 Yava Labs Restock Alert!\n\n"
        f"Product:\n{product_title}\n\n"
        f"Flavor:\n{flavor}\n\n"
        "Status:\n\u2705 In Stock\n\n"
        "Buy Now:\n"
        f"{product_url}\n\n"
        f"Time:\n{timestamp}"
    )

    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": config.telegram_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=config.request_timeout)
        resp.raise_for_status()
        logger.info("Telegram notification sent successfully")
        return True
    except requests.Timeout:
        logger.error("Telegram API request timed out")
        return False
    except requests.RequestException as e:
        logger.error("Failed to send Telegram notification: %s", e)
        return False
