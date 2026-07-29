from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Config:
    product_url: str = (
        "https://www.yavalabs.ae/products/pure-iso-whey-2-kg?variant=46692232495329"
    )
    product_handle: str = "pure-iso-whey-2-kg"
    variant_ids: List[int] = field(default_factory=lambda: [46692232495329])
    product_title: str = "Pure ISO Whey 2 KG"
    variant_names: Dict[int, str] = field(
        default_factory=lambda: {46692232495329: "Banana"}
    )

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
