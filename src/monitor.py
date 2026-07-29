from __future__ import annotations

import argparse
import logging
import sys
from typing import Dict, List

from src.config import Config
from src.notifier import send_telegram_notification
from src.shopify import get_variant_status
from src.state import get_previous_status, load_state, save_state, update_state

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)


def check_variant(
    config: Config, variant_id: int, state: Dict[str, str]
) -> bool:
    variant_info = get_variant_status(config, variant_id)

    current_status = "in_stock" if variant_info.available else "out_of_stock"
    previous_status = get_previous_status(state, variant_id)

    logger.info("Variant %d (%s): current=%s previous=%s",
                variant_id, variant_info.title, current_status, previous_status)

    notified = False

    if previous_status == "out_of_stock" and current_status == "in_stock":
        logger.info(
            "Stock restocked for variant %d (%s)! Sending notification.",
            variant_id,
            variant_info.title,
        )
        flavor = config.variant_names.get(variant_id, variant_info.title)
        if not config.dry_run:
            send_telegram_notification(
                config,
                config.product_title,
                flavor,
                config.product_url,
            )
        else:
            logger.info("[DRY-RUN] Would send notification for %s", flavor)
        notified = True

    elif previous_status == current_status:
        logger.info("No status change for variant %d (%s).", variant_id, variant_info.title)
    elif previous_status is None:
        logger.info(
            "First check for variant %d (%s). Setting initial state to %s.",
            variant_id,
            variant_info.title,
            current_status,
        )

    update_state(state, variant_id, current_status)

    if not config.dry_run:
        save_state(config.state_file, state)
    else:
        logger.info("[DRY-RUN] Would save state: %s", state)

    return notified


def check_all_variants(config: Config) -> bool:
    state = load_state(config.state_file)
    any_notified = False

    for variant_id in config.variant_ids:
        try:
            notified = check_variant(config, variant_id, state)
            if notified:
                any_notified = True
        except Exception as e:
            logger.error("Failed to check variant %d: %s", variant_id, e)
            raise

    return any_notified


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Yava Labs Stock Monitor — Shopify variant stock checker"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending notifications or saving state",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    setup_logging(args.verbose)

    config = Config.from_env(dry_run=args.dry_run, verbose=args.verbose)

    logger.info("Starting stock check for %s", config.product_url)
    logger.info("Variants to monitor: %s", config.variant_ids)

    try:
        notified = check_all_variants(config)
        if notified:
            logger.info("Restock notification sent.")
        else:
            logger.info("No restock detected.")
        return 0
    except Exception as e:
        logger.error("Stock check failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
