from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict

import pytest

from src.shopify import VariantInfo, extract_variant, fetch_product_json, ShopifyError
from src.state import get_previous_status, load_state, save_state, update_state


def _make_product_data(variants: list[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": 9026207580385,
        "title": "Pure Iso Whey 2 kg",
        "handle": "pure-iso-whey-2-kg",
        "variants": variants,
    }


class TestExtractVariant:
    def test_finds_available_variant(self):
        data = _make_product_data([
            {"id": 1, "title": "Vanilla", "available": True},
            {"id": 2, "title": "Banana", "available": False},
        ])
        variant = extract_variant(data, 2)
        assert variant is not None
        assert variant.variant_id == 2
        assert variant.title == "Banana"
        assert variant.available is False
        assert variant.product_title == "Pure Iso Whey 2 kg"

    def test_stock_detection_in_stock(self):
        data = _make_product_data([
            {"id": 1, "title": "Vanilla", "available": True},
        ])
        variant = extract_variant(data, 1)
        assert variant is not None
        assert variant.available is True

    def test_stock_detection_out_of_stock(self):
        data = _make_product_data([
            {"id": 1, "title": "Vanilla", "available": False},
        ])
        variant = extract_variant(data, 1)
        assert variant is not None
        assert variant.available is False

    def test_missing_variant_returns_none(self):
        data = _make_product_data([
            {"id": 1, "title": "Vanilla", "available": True},
        ])
        variant = extract_variant(data, 999)
        assert variant is None

    def test_empty_variants_returns_none(self):
        data = _make_product_data([])
        variant = extract_variant(data, 1)
        assert variant is None

    def test_malformed_json_missing_variants_key(self):
        data: Dict[str, Any] = {"title": "No variants here"}
        variant = extract_variant(data, 1)
        assert variant is None

    def test_missing_available_field_defaults_to_false(self):
        data = _make_product_data([
            {"id": 1, "title": "Vanilla"},
        ])
        variant = extract_variant(data, 1)
        assert variant is not None
        assert variant.available is False


class TestStateTransitions:
    def _make_state_file(self, content: Dict[str, str]) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            json.dump(content, f)
        return path

    def test_load_state_returns_empty_when_file_missing(self):
        state = load_state("/tmp/nonexistent_file_12345.json")
        assert state == {}

    def test_load_state_returns_content(self):
        path = self._make_state_file({"123": "out_of_stock"})
        try:
            state = load_state(path)
            assert state == {"123": "out_of_stock"}
        finally:
            os.unlink(path)

    def test_load_state_handles_corrupted_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            f.write("not json")
        try:
            state = load_state(path)
            assert state == {}
        finally:
            os.unlink(path)

    def test_get_previous_status_returns_none_for_new_variant(self):
        state = {"123": "out_of_stock"}
        assert get_previous_status(state, 456) is None

    def test_get_previous_status_returns_value(self):
        state = {"123": "out_of_stock"}
        assert get_previous_status(state, 123) == "out_of_stock"

    def test_update_state_sets_value(self):
        state: Dict[str, str] = {}
        update_state(state, 123, "in_stock")
        assert state == {"123": "in_stock"}

    def test_update_state_overwrites(self):
        state = {"123": "out_of_stock"}
        update_state(state, 123, "in_stock")
        assert state == {"123": "in_stock"}

    def test_save_and_load_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            state = {"123": "in_stock", "456": "out_of_stock"}
            save_state(path, state)
            loaded = load_state(path)
            assert loaded == state
        finally:
            os.unlink(path)


class TestVariantInfoDataclass:
    def test_variant_info_creation(self):
        v = VariantInfo(
            variant_id=46692232495329,
            title="Banana",
            available=False,
            product_title="Pure Iso Whey 2 kg",
        )
        assert v.variant_id == 46692232495329
        assert v.title == "Banana"
        assert v.available is False
        assert v.product_title == "Pure Iso Whey 2 kg"


class TestFetchProductJsonErrors:
    def test_invalid_url_raises_error(self, monkeypatch):
        from src import config as cfg_module

        cfg = cfg_module.Config(max_retries=1)
        url = "https://www.yavalabs.ae/products/this-does-not-exist-12345"
        with pytest.raises(ShopifyError):
            fetch_product_json(url, cfg)
