"""
Unit Test Suite for OmniPrice Pro Engine & Algorithmic Repricer.
Tests margin guards, dynamic repricing strategies, perceptual hashing, and exports.
"""

import io
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from PIL import Image
import pandas as pd
from engine import (
    calculate_repricing,
    compute_dhash,
    hamming_distance,
    hash_similarity_score,
    export_shopify_csv,
    export_excel_report,
    generate_catalog_template,
    parse_uploaded_catalog
)
from scraper import CompetitorScraper, simulate_marketplace_benchmark


def test_beat_lowest_strategy():
    """Test that beat_lowest undercuts lowest competitor by target offset."""
    outcome = calculate_repricing(
        cost_price=100.0,
        current_price=150.0,
        competitor_prices=[140.0, 145.0, 150.0],
        strategy="beat_lowest",
        target_offset_pct=2.0,
        floor_margin_pct=15.0
    )
    # min comp = 140. 140 * (1 - 0.02) = 137.2
    assert outcome.suggested_price == 137.20
    assert outcome.suggested_price < 140.0
    assert outcome.new_margin_pct > 15.0
    assert "BuyBox" in outcome.status


def test_match_lowest_strategy():
    """Test matching exact lowest competitor price."""
    outcome = calculate_repricing(
        cost_price=100.0,
        current_price=150.0,
        competitor_prices=[135.50, 140.0],
        strategy="match_lowest",
        floor_margin_pct=15.0
    )
    assert outcome.suggested_price == 135.50
    assert "BuyBox" in outcome.status or "Optimal" in outcome.status


def test_fixed_margin_strategy():
    """Test pricing based on fixed markup above cost price."""
    outcome = calculate_repricing(
        cost_price=200.0,
        current_price=260.0,
        competitor_prices=[280.0],
        strategy="fixed_margin",
        target_offset_pct=25.0,
        floor_margin_pct=15.0
    )
    # 200 * (1 + 0.25) = 250.0
    assert outcome.suggested_price == 250.00
    assert "Optimal" in outcome.status or "BuyBox" in outcome.status


def test_floor_margin_guard_protection():
    """Test that price war cannot breach floor margin guard."""
    # Competitor offers dumping price 105, but cost is 100 and floor margin is 20% (floor price = 120)
    outcome = calculate_repricing(
        cost_price=100.0,
        current_price=150.0,
        competitor_prices=[105.0],
        strategy="beat_lowest",
        target_offset_pct=2.0,
        floor_margin_pct=20.0
    )
    # Suggested must NOT go below 120.00
    assert outcome.suggested_price == 120.00
    assert outcome.status == "🛡️ Floor Protected"
    assert "Clamped to minimum safe margin" in outcome.action_note


def test_perceptual_dhash_identical():
    """Test that identical images have 0 hamming distance and 100% similarity."""
    img1 = Image.new("RGB", (100, 100), color=(50, 100, 150))
    img2 = Image.new("RGB", (100, 100), color=(50, 100, 150))
    
    h1 = compute_dhash(img1)
    h2 = compute_dhash(img2)
    
    dist = hamming_distance(h1, h2)
    sim = hash_similarity_score(h1, h2)
    
    assert dist == 0
    assert sim == 1.0


def test_catalog_template_and_parsing():
    """Test Excel template generation and subsequent catalog parsing."""
    template_bytes = generate_catalog_template()
    assert len(template_bytes) > 0
    
    parsed = parse_uploaded_catalog(template_bytes, "template.xlsx")
    assert len(parsed) == 5
    assert parsed[0]["SKU"] == "TECH-001"
    assert parsed[0]["Cost Price"] == 850.0
    assert "Our Image Hash" in parsed[0]


def test_shopify_and_excel_exports():
    """Test export pipelines for Shopify and styled Excel."""
    df = pd.DataFrame([{
        "SKU": "TEST-1",
        "Title": "Test Product One",
        "Category": "Test",
        "Cost Price": 50.0,
        "Our Price": 70.0,
        "Competitor Min": 68.0,
        "Suggested Price": 66.50,
        "Price Delta ($)": -3.50,
        "New Margin %": 24.8,
        "Margin Amount": 16.50,
        "Reprice Status": "⚡ Beat Lowest",
        "Action Note": "Optimal test"
    }])
    
    csv_bytes = export_shopify_csv(df)
    assert b"Handle,Title,Variant SKU" in csv_bytes
    assert b"TEST-1" in csv_bytes
    
    excel_bytes = export_excel_report(df)
    assert len(excel_bytes) > 1000


def test_scraper_schema_extraction():
    """Test HTML schema extraction fallback."""
    sample_html = """
    <html>
      <head>
        <title>Samsung Galaxy S24 Ultra — Prom.ua</title>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org/",
          "@type": "Product",
          "name": "Samsung Galaxy S24 Ultra 256GB Titanium Gray",
          "offers": {
            "@type": "Offer",
            "price": "43999.00",
            "priceCurrency": "UAH",
            "availability": "https://schema.org/InStock"
          }
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    scraper = CompetitorScraper()
    res = scraper.extract_from_html(sample_html, source_url="https://prom.ua/p123-s24.html")
    assert res["price"] == 43999.0
    assert "Samsung Galaxy" in res["title"]
    assert res["currency"] == "UAH"
    assert res["in_stock"] is True
