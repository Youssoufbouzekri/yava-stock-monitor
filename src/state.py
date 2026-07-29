from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def load_state(state_file: str) -> Dict[str, str]:
    if not os.path.exists(state_file):
        logger.info("State file %s not found, starting fresh", state_file)
        return {}

    try:
        with open(state_file, "r") as f:
            data: Dict[str, str] = json.load(f)
        logger.info("Loaded state from %s: %s", state_file, data)
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load state file %s: %s", state_file, e)
        return {}


def save_state(state_file: str, state: Dict[str, str]) -> None:
    try:
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        logger.info("State saved to %s", state_file)
    except OSError as e:
        logger.error("Failed to save state to %s: %s", state_file, e)
        raise


def get_previous_status(
    state: Dict[str, str], variant_id: int
) -> Optional[str]:
    key = str(variant_id)
    return state.get(key)


def update_state(
    state: Dict[str, str], variant_id: int, status: str
) -> Dict[str, str]:
    state[str(variant_id)] = status
    return state
