"""
OmniPrice Scraper — Real-time Competitor Scraping & Price Extraction Engine.
Supports Rozetka, Prom.ua, Amazon, Shopify stores, and generic E-Commerce schema.org parsing.
"""

import re
import json
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import urllib.request
import urllib.error


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]


class CompetitorScraper:
    """Production-grade price extractor with schema.org JSON-LD and regex fallback."""

    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def extract_from_html(self, html: str, source_url: str = "") -> Dict[str, Any]:
        """Extracts product title, price, currency, and availability from raw HTML."""
        title = ""
        price = 0.0
        currency = "UAH"
        in_stock = True

        # 1. Try Schema.org JSON-LD
        json_ld_matches = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        for match in json_ld_matches:
            try:
                data = json.loads(match.strip())
                # Handle @graph or direct Product
                items = data.get("@graph", [data]) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for item in items:
                    if isinstance(item, dict) and item.get("@type") in ["Product", "IndividualProduct"]:
                        title = item.get("name", title)
                        offers = item.get("offers", {})
                        if isinstance(offers, list) and offers:
                            offers = offers[0]
                        if isinstance(offers, dict):
                            raw_p = offers.get("price") or offers.get("lowPrice")
                            if raw_p:
                                price = float(str(raw_p).replace(",", ".").replace(" ", ""))
                            currency = offers.get("priceCurrency", currency)
                            avail = str(offers.get("availability", "")).lower()
                            in_stock = "instock" in avail or not ("outofstock" in avail)
                        break
            except Exception:
                continue

        # 2. OpenGraph Fallback for Title
        if not title:
            og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if og_title:
                title = og_title.group(1).strip()
            else:
                title_tag = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                if title_tag:
                    title = title_tag.group(1).split("|")[0].split("—")[0].strip()

        # 3. OpenGraph / Meta Fallback for Price
        if price <= 0:
            og_price = re.search(r'<meta[^>]+property=["\']product:price:amount["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if og_price:
                try:
                    price = float(og_price.group(1).replace(",", "."))
                except ValueError:
                    pass

        # 4. Regex Pattern Matching for Common Ukrainian / EU E-commerce
        if price <= 0:
            price_patterns = [
                r'class="[^"]*(?:product-price__big|price-value|current-price|product-price)[^"]*"[^>]*>([\d\s.,]+)',
                r'itemprop="price"[^>]*content="([\d.]+)"',
                r'data-price="([\d.]+)"'
            ]
            for pat in price_patterns:
                m = re.search(pat, html, re.IGNORECASE)
                if m:
                    clean_str = re.sub(r'[^\d.]', '', m.group(1).replace(",", "."))
                    try:
                        price = float(clean_str)
                        break
                    except ValueError:
                        pass

        domain = urlparse(source_url).netloc if source_url else "competitor.com"
        return {
            "title": title or "Sample Product Listing",
            "price": price,
            "currency": currency,
            "in_stock": in_stock,
            "domain": domain,
            "source_url": source_url
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Fetches live competitor product URL and returns structured price telemetry."""
        start_time = time.time()
        headers = {
            "User-Agent": USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                parsed = self.extract_from_html(html, source_url=url)
                parsed["latency_ms"] = int((time.time() - start_time) * 1000)
                parsed["status"] = "success"
                return parsed
        except Exception as e:
            return {
                "title": "Failed to resolve listing",
                "price": 0.0,
                "currency": "UAH",
                "in_stock": False,
                "domain": urlparse(url).netloc,
                "source_url": url,
                "latency_ms": int((time.time() - start_time) * 1000),
                "status": "error",
                "error": str(e)
            }


def simulate_marketplace_benchmark(product_title: str) -> List[Dict[str, Any]]:
    """Simulates real-world multi-marketplace price check across Rozetka, Prom, and Epicentr."""
    base_hash = abs(hash(product_title))
    p1 = 300.0 + (base_hash % 200)
    p2 = p1 * 0.96
    p3 = p1 * 1.04
    
    return [
        {
            "marketplace": "Rozetka",
            "merchant": "Rozetka Official",
            "price": round(p2, 2),
            "currency": "UAH",
            "availability": "В наявності",
            "shipping": "Безкоштовно у відділення",
            "status": "active"
        },
        {
            "marketplace": "Prom.ua",
            "merchant": "TopTech Ukraine",
            "price": round(p1, 2),
            "currency": "UAH",
            "availability": "В наявності",
            "shipping": "Нова Пошта 1-2 дні",
            "status": "active"
        },
        {
            "marketplace": "EpicentrK",
            "merchant": "Епіцентр Маркет",
            "price": round(p3, 2),
            "currency": "UAH",
            "availability": "Під замовлення",
            "shipping": "Самовивіз",
            "status": "active"
        }
    ]
