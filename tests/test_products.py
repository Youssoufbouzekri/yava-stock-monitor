from __future__ import annotations

from src.products import PRODUCTS


class TestProductsConfig:
    def test_products_is_nonempty_list(self):
        assert isinstance(PRODUCTS, list)
        assert len(PRODUCTS) > 0

    def test_each_product_has_required_keys(self):
        for product in PRODUCTS:
            assert "name" in product
            assert "url" in product
            assert "variants" in product
            assert isinstance(product["name"], str)
            assert isinstance(product["url"], str)
            assert isinstance(product["variants"], list)

    def test_each_variant_has_required_keys(self):
        for product in PRODUCTS:
            for variant in product["variants"]:
                assert "name" in variant
                assert "id" in variant
                assert isinstance(variant["name"], str)
                assert isinstance(variant["id"], int)

    def test_variant_ids_are_unique(self):
        seen = set()
        for product in PRODUCTS:
            for variant in product["variants"]:
                vid = variant["id"]
                assert vid not in seen, f"Duplicate variant id: {vid}"
                seen.add(vid)

    def test_product_urls_are_well_formed(self):
        for product in PRODUCTS:
            url = product["url"]
            assert url.startswith("https://"), f"URL must use HTTPS: {url}"
            assert "/products/" in url, f"URL must contain /products/: {url}"
