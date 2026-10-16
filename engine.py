"""
OmniPrice Engine — Algorithmic Repricing, Margin Guard, and Visual Matcher.
Core algorithmic layer for E-Commerce Price Intelligence.
"""

import io
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side


def compute_dhash(image: Image.Image, hash_size: int = 8) -> int:
    """Computes a 64-bit difference hash (dHash) for an image."""
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    
    diff = []
    for row in range(hash_size):
        row_offset = row * (hash_size + 1)
        for col in range(hash_size):
            p1 = pixels[row_offset + col]
            p2 = pixels[row_offset + col + 1]
            diff.append(1 if p1 > p2 else 0)
            
    hash_int = 0
    for bit in diff:
        hash_int = (hash_int << 1) | bit
    return hash_int


def hamming_distance(h1: int, h2: int) -> int:
    """Calculates number of differing bits between two 64-bit hashes."""
    x = h1 ^ h2
    dist = 0
    while x > 0:
        dist += x & 1
        x >>= 1
    return dist


def hash_similarity_score(h1: int, h2: int, bit_length: int = 64) -> float:
    """Converts Hamming distance into a normalized similarity score (0.0 to 1.0)."""
    dist = hamming_distance(h1, h2)
    return max(0.0, 1.0 - (dist / bit_length))


@dataclass
class RepriceOutcome:
    suggested_price: float
    current_margin_pct: float
    new_margin_pct: float
    margin_amount: float
    status: str
    status_color: str
    action_note: str


def calculate_repricing(
    cost_price: float,
    current_price: float,
    competitor_prices: List[float],
    strategy: str = "beat_lowest",
    target_offset_pct: float = 2.0,
    floor_margin_pct: float = 15.0
) -> RepriceOutcome:
    """
    Computes optimal price using market benchmarks and profit margin guardrails.
    
    Strategies:
    - 'beat_lowest': Price below lowest active competitor by target_offset_pct.
    - 'match_lowest': Exactly match lowest competitor.
    - 'fixed_margin': Cost + target_offset_pct profit margin.
    """
    valid_comp_prices = [p for p in competitor_prices if p > 0]
    min_comp_price = min(valid_comp_prices) if valid_comp_prices else current_price
    
    current_margin = ((current_price - cost_price) / current_price) * 100 if current_price > 0 else 0.0
    floor_price = cost_price * (1.0 + (floor_margin_pct / 100.0))
    
    if strategy == "beat_lowest":
        raw_target = min_comp_price * (1.0 - (target_offset_pct / 100.0))
    elif strategy == "match_lowest":
        raw_target = min_comp_price
    elif strategy == "fixed_margin":
        raw_target = cost_price * (1.0 + (target_offset_pct / 100.0))
    else:
        raw_target = current_price

    # Round to standard commercial 9-ending or clean float (e.g. 249.00 or .99)
    suggested = round(raw_target, 2)
    
    # Floor margin guard enforcement
    if suggested < floor_price:
        suggested = round(floor_price, 2)
        new_margin = ((suggested - cost_price) / suggested) * 100
        margin_amt = suggested - cost_price
        return RepriceOutcome(
            suggested_price=suggested,
            current_margin_pct=current_margin,
            new_margin_pct=new_margin,
            margin_amount=margin_amt,
            status="🛡️ Floor Protected",
            status_color="#F59E0B",
            action_note=f"Competitor too low ({min_comp_price:.2f}). Clamped to minimum safe margin {floor_margin_pct:.0f}%."
        )
        
    new_margin = ((suggested - cost_price) / suggested) * 100
    margin_amt = suggested - cost_price
    
    if valid_comp_prices and current_price > min_comp_price and suggested <= min_comp_price:
        return RepriceOutcome(
            suggested_price=suggested,
            current_margin_pct=current_margin,
            new_margin_pct=new_margin,
            margin_amount=margin_amt,
            status="🟢 BuyBox Recovered",
            status_color="#10B981",
            action_note=f"Undercut competitor ({min_comp_price:.2f}) while maintaining healthy {new_margin:.1f}% margin."
        )
    elif valid_comp_prices and current_price <= min_comp_price:
        return RepriceOutcome(
            suggested_price=suggested,
            current_margin_pct=current_margin,
            new_margin_pct=new_margin,
            margin_amount=margin_amt,
            status="✓ Optimal Price",
            status_color="#38BDF8",
            action_note="Currently competitive. Margin preserved."
        )
    else:
        return RepriceOutcome(
            suggested_price=suggested,
            current_margin_pct=current_margin,
            new_margin_pct=new_margin,
            margin_amount=margin_amt,
            status="🟡 Rebalanced",
            status_color="#818CF8",
            action_note=f"Target margin adjusted to {new_margin:.1f}%."
        )


def export_shopify_csv(df: pd.DataFrame) -> bytes:
    """Exports dataframe formatted strictly to Shopify CSV Product Update format."""
    shopify_rows = []
    for _, row in df.iterrows():
        sku = str(row.get("SKU", ""))
        handle = re.sub(r"[^a-z0-9]+", "-", str(row.get("Title", "")).lower()).strip("-")
        suggested = row.get("Suggested Price", row.get("Our Price", 0.0))
        current = row.get("Our Price", 0.0)
        
        shopify_rows.append({
            "Handle": handle,
            "Title": row.get("Title", ""),
            "Variant SKU": sku,
            "Variant Price": f"{suggested:.2f}",
            "Variant Compare At Price": f"{current:.2f}" if suggested < current else "",
            "Cost per item": f"{row.get('Cost Price', 0.0):.2f}",
            "Status": "active"
        })
        
    out_df = pd.DataFrame(shopify_rows)
    csv_buffer = io.StringIO()
    out_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")


def export_excel_report(df: pd.DataFrame) -> bytes:
    """Generates a styled Excel workbook with margin highlights and summary cards."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Price Intelligence Summary"
    
    # Headers
    headers = [
        "SKU", "Product Title", "Category", "Cost Price", 
        "Our Current Price", "Comp Lowest", "Suggested Price", 
        "New Margin %", "Margin Amount", "Status"
    ]
    ws.append(headers)
    
    # Styling definitions
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for _, r in df.iterrows():
        row_vals = [
            r.get("SKU", ""),
            r.get("Title", ""),
            r.get("Category", ""),
            r.get("Cost Price", 0.0),
            r.get("Our Price", 0.0),
            r.get("Competitor Min", 0.0),
            r.get("Suggested Price", 0.0),
            r.get("New Margin %", 0.0),
            r.get("Margin Amount", 0.0),
            r.get("Reprice Status", "")
        ]
        ws.append(row_vals)
        curr_row = ws.max_row
        
        # Format currency & percent
        ws.cell(row=curr_row, column=4).number_format = "$#,##0.00"
        ws.cell(row=curr_row, column=5).number_format = "$#,##0.00"
        ws.cell(row=curr_row, column=6).number_format = "$#,##0.00"
        ws.cell(row=curr_row, column=7).number_format = "$#,##0.00"
        ws.cell(row=curr_row, column=8).number_format = "0.0%"
        ws.cell(row=curr_row, column=9).number_format = "$#,##0.00"
        
        for c_idx in range(1, len(headers) + 1):
            ws.cell(row=curr_row, column=c_idx).border = thin_border
            
    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    return excel_buffer.getvalue()
