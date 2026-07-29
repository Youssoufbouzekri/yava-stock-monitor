from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from src.config import Config

logger = logging.getLogger(__name__)


class ShopifyError(Exception):
    pass


@dataclass
class VariantInfo:
    variant_id: int
    title: str
    available: bool
    product_title: str
    option_name: str = ""


def _build_js_url(config: Config) -> str:
    base = config.product_url.split("?")[0].rstrip("/")
    return f"{base}.js"


def fetch_product_json(config: Config) -> Dict[str, Any]:
    url = _build_js_url(config)
    logger.info("Fetching product JSON from %s", url)

    session = requests.Session()
    session.headers.update({"User-Agent": config.user_agent})

    last_error: Optional[Exception] = None

    for attempt in range(1, config.max_retries + 1):
        try:
            resp = session.get(url, timeout=config.request_timeout)
            if resp.status_code == 429:
                wait = config.retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited (429). Retrying in %.1fs (attempt %d/%d)",
                    wait,
                    attempt,
                    config.max_retries,
                )
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = config.retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    "Server error %d. Retrying in %.1fs (attempt %d/%d)",
                    resp.status_code,
                    wait,
                    attempt,
                    config.max_retries,
                )
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
            logger.info("Product JSON fetched successfully")
            return data
        except requests.Timeout:
            last_error = ShopifyError(
                f"Request timed out after {config.request_timeout}s"
            )
            wait = config.retry_delay * (2 ** (attempt - 1))
            logger.warning(
                "Timeout. Retrying in %.1fs (attempt %d/%d)",
                wait,
                attempt,
                config.max_retries,
            )
            time.sleep(wait)
        except requests.RequestException as e:
            last_error = ShopifyError(f"HTTP request failed: {e}")
            wait = config.retry_delay * (2 ** (attempt - 1))
            logger.warning(
                "Request failed: %s. Retrying in %.1fs (attempt %d/%d)",
                e,
                wait,
                attempt,
                config.max_retries,
            )
            time.sleep(wait)
        except ValueError as e:
            raise ShopifyError(f"Invalid JSON response: {e}") from e

    raise ShopifyError(
        f"Failed to fetch product data after {config.max_retries} attempts"
    ) from last_error


def extract_variant(
    product_data: Dict[str, Any], variant_id: int
) -> Optional[VariantInfo]:
    variants: List[Dict[str, Any]] = product_data.get("variants", [])
    product_title: str = product_data.get("title", "Unknown Product")

    if not variants:
        logger.warning("No variants found in product data")
        return None

    for v in variants:
        if v.get("id") == variant_id:
            title: str = v.get("title", "Unknown")
            available: bool = bool(v.get("available", False))
            logger.info("Variant found: id=%d title=%s available=%s", variant_id, title, available)
            return VariantInfo(
                variant_id=variant_id,
                title=title,
                available=available,
                product_title=product_title,
            )

    logger.warning("Variant %d not found in product data", variant_id)
    return None


def get_variant_status(config: Config, variant_id: int) -> VariantInfo:
    product_data = fetch_product_json(config)
    variant = extract_variant(product_data, variant_id)

    if variant is None:
        raise ShopifyError(
            f"Variant {variant_id} not found in product '{config.product_handle}'"
        )

    return variant
