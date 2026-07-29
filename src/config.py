from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    state_file: str = "state.json"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    request_timeout: int = 10
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    max_retries: int = 3
    retry_delay: float = 2.0

    dry_run: bool = False
    verbose: bool = False

    @classmethod
    def from_env(cls, dry_run: bool = False, verbose: bool = False) -> Config:
        return cls(
            telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
            dry_run=dry_run,
            verbose=verbose,
        )
