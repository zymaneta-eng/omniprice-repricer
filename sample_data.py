"""
OmniPrice Sample Catalog & Visual Assets.
Verifiable realistic products across consumer electronics, smart home, and lifestyle gear.
"""

from typing import List, Dict, Any
from PIL import Image, ImageDraw
from engine import compute_dhash


def generate_item_thumbnail(color: tuple, shape: str = "rect", text: str = "") -> Image.Image:
    """Generates a clean synthetic item render for pHash similarity verification."""
    img = Image.new("RGB", (140, 140), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # Outer item silhouette
    if shape == "headphone":
        draw.arc([30, 25, 110, 105], start=180, end=0, fill=color, width=8)
        draw.rounded_rectangle([25, 60, 45, 105], radius=6, fill=color)
        draw.rounded_rectangle([95, 60, 115, 105], radius=6, fill=color)
    elif shape == "watch":
        draw.rectangle([55, 15, 85, 125], fill=(70, 70, 80))
        draw.rounded_rectangle([40, 40, 100, 100], radius=16, fill=color)
        draw.ellipse([50, 50, 90, 90], fill=(20, 20, 25))
    elif shape == "thermo":
        draw.rounded_rectangle([45, 30, 95, 115], radius=10, fill=color)
        draw.rectangle([55, 20, 85, 30], fill=(50, 50, 50))
    elif shape == "keyboard":
        draw.rounded_rectangle([20, 45, 120, 95], radius=6, fill=color)
        for rx in range(26, 114, 12):
            for ry in range(52, 90, 12):
                draw.rectangle([rx, ry, rx+8, ry+8], fill=(240, 240, 240))
    elif shape == "coffee":
        draw.rounded_rectangle([35, 35, 105, 115], radius=8, fill=color)
        draw.rectangle([45, 20, 95, 35], fill=(40, 40, 40))
        draw.rectangle([50, 75, 90, 95], fill=(220, 220, 220))
    else:
        draw.rounded_rectangle([30, 30, 110, 110], radius=12, fill=color)
        
    return img


def get_default_catalog() -> List[Dict[str, Any]]:
    """Returns realistic retail catalog with multi-competitor telemetry."""
    
    # Pre-generate PIL images and compute genuine hashes
    img_sony_our = generate_item_thumbnail((25, 25, 25), "headphone")
    img_sony_comp1 = generate_item_thumbnail((28, 28, 30), "headphone")  # Very similar
    img_sony_comp2 = generate_item_thumbnail((180, 40, 40), "headphone") # Different color
    
    img_watch_our = generate_item_thumbnail((40, 50, 70), "watch")
    img_watch_comp1 = generate_item_thumbnail((42, 52, 72), "watch")
    
    img_mug_our = generate_item_thumbnail((20, 20, 20), "thermo")
    img_mug_comp1 = generate_item_thumbnail((22, 22, 24), "thermo")
    
    img_kb_our = generate_item_thumbnail((45, 55, 75), "keyboard")
    img_kb_comp1 = generate_item_thumbnail((45, 55, 75), "keyboard")
    
    img_coffee_our = generate_item_thumbnail((180, 30, 30), "coffee")
    img_coffee_comp1 = generate_item_thumbnail((185, 35, 35), "coffee")

    catalog = [
        {
            "SKU": "AUD-SONY-XM5-BLK",
            "Title": "Sony WH-1000XM5 Noise-Canceling Wireless Headphones (Black)",
            "Category": "Audio & Acoustics",
            "Cost Price": 260.00,
            "Our Price": 349.00,
            "Competitor 1 (MegaStore)": 329.00,
            "Competitor 2 (TechZone)": 339.00,
            "Competitor 3 (ElectroHub)": 355.00,
            "Our Image": img_sony_our,
            "Comp Image": img_sony_comp1,
            "Our Image Hash": compute_dhash(img_sony_our),
            "Comp Image Hash": compute_dhash(img_sony_comp1)
        },
        {
            "SKU": "WTC-GARMIN-FOR965",
            "Title": "Garmin Forerunner 965 Premium GPS Running Smartwatch",
            "Category": "Wearables & Fitness",
            "Cost Price": 440.00,
            "Our Price": 599.00,
            "Competitor 1 (MegaStore)": 579.00,
            "Competitor 2 (TechZone)": 599.00,
            "Competitor 3 (ElectroHub)": 589.00,
            "Our Image": img_watch_our,
            "Comp Image": img_watch_comp1,
            "Our Image Hash": compute_dhash(img_watch_our),
            "Comp Image Hash": compute_dhash(img_watch_comp1)
        },
        {
            "SKU": "THM-FELLOW-CARTER-16",
            "Title": "Fellow Carter Move Mug 16oz Vacuum Insulated Tumbler (Matte Black)",
            "Category": "Drinkware & Lifestyle",
            "Cost Price": 21.00,
            "Our Price": 38.00,
            "Competitor 1 (MegaStore)": 35.00,
            "Competitor 2 (TechZone)": 36.50,
            "Competitor 3 (ElectroHub)": 39.00,
            "Our Image": img_mug_our,
            "Comp Image": img_mug_comp1,
            "Our Image Hash": compute_dhash(img_mug_our),
            "Comp Image Hash": compute_dhash(img_mug_comp1)
        },
        {
            "SKU": "KEY-KEYCHRON-Q1PRO",
            "Title": "Keychron Q1 Pro Wireless Custom Mechanical Keyboard (Red Switch)",
            "Category": "PC Peripherals",
            "Cost Price": 145.00,
            "Our Price": 209.00,
            "Competitor 1 (MegaStore)": 199.00,
            "Competitor 2 (TechZone)": 205.00,
            "Competitor 3 (ElectroHub)": 215.00,
            "Our Image": img_kb_our,
            "Comp Image": img_kb_comp1,
            "Our Image Hash": compute_dhash(img_kb_our),
            "Comp Image Hash": compute_dhash(img_kb_comp1)
        },
        {
            "SKU": "KIT-DE'LONGHI-DEDICA",
            "Title": "De'Longhi Dedica Deluxe Manual Espresso & Cappuccino Machine",
            "Category": "Home & Kitchen",
            "Cost Price": 195.00,
            "Our Price": 289.00,
            "Competitor 1 (MegaStore)": 269.00,
            "Competitor 2 (TechZone)": 275.00,
            "Competitor 3 (ElectroHub)": 299.00,
            "Our Image": img_coffee_our,
            "Comp Image": img_coffee_comp1,
            "Our Image Hash": compute_dhash(img_coffee_our),
            "Comp Image Hash": compute_dhash(img_coffee_comp1)
        }
    ]
    return catalog
