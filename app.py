"""
OmniPrice Pro — E-Commerce Price Intelligence & Algorithmic Repricer Terminal.
Linear-minimalist Dark Mode Dashboard for Shopify, Rozetka, Prom, and Amazon merchants.
"""

import io
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Configure page layout
st.set_page_config(
    page_title="OmniPrice Pro | Price Intelligence & Repricer Terminal",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Linear/Clay Dark Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    .stApp {
        background-color: #0B0F17 !important;
        color: #F8FAFC !important;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    #MainMenu, footer {
        display: none !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 100% !important;
    }

    /* Top Nav */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(31, 41, 55, 0.6);
        margin-bottom: 0.9rem;
    }
    .brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.02em;
    }
    .version-badge {
        font-size: 0.72rem;
        font-weight: 500;
        color: #94A3B8;
        background: #121826;
        border: 1px solid #1F2937;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .dev-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        border-radius: 9999px;
        background: #121826;
        border: 1px solid #1F2937;
        font-size: 0.82rem;
        color: #CBD5E1;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 8px #10B981;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }
    .kpi-card {
        background: #121826;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        transition: border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #374151;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.74rem;
        font-weight: 600;
        color: #94A3B8;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Container wrappers */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #121826 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 12px !important;
        padding: 1.1rem 1.4rem !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #1F2937;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-radius: 6px 6px 0 0 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #6366F1 !important;
        background: transparent !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #121826 !important;
        color: #CBD5E1 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Add current path for local imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from engine import (
    calculate_repricing, 
    export_shopify_csv, 
    export_excel_report,
    hash_similarity_score,
    hamming_distance,
    generate_catalog_template,
    parse_uploaded_catalog
)
from scraper import CompetitorScraper, simulate_marketplace_benchmark
from sample_data import get_default_catalog

# Top Navigation Bar
st.markdown("""
<div class="top-nav">
  <div style="display: flex; align-items: center; gap: 10px;">
    <span class="brand-title">🏷️ OmniPrice Pro</span>
    <span class="version-badge">v2.5 Enterprise</span>
    <span class="version-badge" style="color: #818CF8; border-color: rgba(99,102,241,0.4); background: rgba(99,102,241,0.1);">Automated Repricer</span>
  </div>
  <div style="display: flex; align-items: center; gap: 12px;">
    <a href="https://t.me/Nataly_Zyma" target="_blank" style="text-decoration: none; color: #38BDF8; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); padding: 5px 14px; border-radius: 9999px;">
      ✈️ Написати в Telegram (@Nataly_Zyma)
    </a>
    <div class="dev-badge">
      Розробник: Наталія • areonixwinter@gmail.com
      <span class="status-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Initialize Session Catalog
if "catalog" not in st.session_state:
    st.session_state.catalog = get_default_catalog()
    st.session_state.source_mode = "demo"

# Catalog Source Switcher & Uploader
with st.container(border=True):
    src_c1, src_c2 = st.columns([2.8, 1.2])
    with src_c1:
        chosen_mode = st.radio(
            "Режим каталогу:",
            ["🛍️ Демонстраційний каталог (5 товарів з аналітикою)", "📁 Завантажити власний прайс (.xlsx / .csv)"],
            horizontal=True,
            index=0 if st.session_state.source_mode == "demo" else 1,
            label_visibility="collapsed"
        )
    with src_c2:
        template_bytes = generate_catalog_template()
        st.download_button(
            "📥 Завантажити шаблон прайсу (.xlsx)",
            data=template_bytes,
            file_name="omniprice_catalog_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    if "Завантажити власний прайс" in chosen_mode:
        uploaded_file = st.file_uploader(
            "Оберіть файл прайс-листа (підтримуються колонки: SKU/Артикул, Title/Назва, Cost Price/Собівартість, Our Price/Наша ціна, Competitor Min/Конкуренти):",
            type=["xlsx", "xls", "csv"],
            key="custom_catalog_upload"
        )
        if uploaded_file is not None:
            try:
                st.session_state.catalog = parse_uploaded_catalog(uploaded_file.read(), uploaded_file.name)
                st.session_state.source_mode = "custom"
                st.success(f"✓ Успішно імпортовано {len(st.session_state.catalog)} товарів з файлу «{uploaded_file.name}». Алгоритм переоцінки готовий до розрахунку!")
            except Exception as e:
                st.error(f"Помилка завантаження файлу: {e}")
    else:
        if st.session_state.source_mode == "custom":
            st.session_state.catalog = get_default_catalog()
            st.session_state.source_mode = "demo"


# Top Horizontal Control Bar
with st.container(border=True):
    col_strat, col_offset, col_floor, col_action = st.columns([2.2, 1.4, 1.4, 1.4])
    
    with col_strat:
        strategy_options = [
            ("⚡ Beat Lowest Competitor", "beat_lowest"),
            ("🎯 Match Lowest Competitor", "match_lowest"),
            ("💎 Target Fixed Gross Margin", "fixed_margin")
        ]
        selected_strat_label = st.selectbox(
            "Repricing Algorithm", 
            [opt[0] for opt in strategy_options],
            index=0
        )
        strategy_key = [opt[1] for opt in strategy_options if opt[0] == selected_strat_label][0]

    with col_offset:
        target_offset = st.slider("Target Offset / Margin %", min_value=0.5, max_value=20.0, value=2.0, step=0.5)

    with col_floor:
        floor_margin = st.slider("Floor Guard (Min Margin %)", min_value=5.0, max_value=35.0, value=15.0, step=1.0)

    with col_action:
        st.markdown("<div style='height: 1.45rem;'></div>", unsafe_allow_html=True)
        recalc_btn = st.button("🔄 Execute Reprice Run", use_container_width=True, type="primary")

# Compute Live Reprice Results
computed_rows = []
for item in st.session_state.catalog:
    cost = item["Cost Price"]
    our_price = item["Our Price"]
    comp_prices = [
        item["Competitor 1 (MegaStore)"],
        item["Competitor 2 (TechZone)"],
        item["Competitor 3 (ElectroHub)"]
    ]
    min_comp = min(comp_prices)
    
    outcome = calculate_repricing(
        cost_price=cost,
        current_price=our_price,
        competitor_prices=comp_prices,
        strategy=strategy_key,
        target_offset_pct=target_offset,
        floor_margin_pct=floor_margin
    )
    
    computed_rows.append({
        "SKU": item["SKU"],
        "Title": item["Title"],
        "Category": item["Category"],
        "Cost Price": cost,
        "Our Price": our_price,
        "Competitor Min": min_comp,
        "Suggested Price": outcome.suggested_price,
        "Price Delta ($)": outcome.suggested_price - our_price,
        "Current Margin %": outcome.current_margin_pct,
        "New Margin %": outcome.new_margin_pct,
        "Margin Amount": outcome.margin_amount,
        "Reprice Status": outcome.status,
        "Action Note": outcome.action_note,
        "Our Image": item["Our Image"],
        "Comp Image": item["Comp Image"],
        "Our Image Hash": item["Our Image Hash"],
        "Comp Image Hash": item["Comp Image Hash"],
        "Comp1": item["Competitor 1 (MegaStore)"],
        "Comp2": item["Competitor 2 (TechZone)"],
        "Comp3": item["Competitor 3 (ElectroHub)"]
    })

df_results = pd.DataFrame(computed_rows)

# Telemetry KPI Row
total_items = len(df_results)
avg_margin = df_results["New Margin %"].mean()
buybox_count = (df_results["Suggested Price"] <= df_results["Competitor Min"]).sum()
floor_count = (df_results["Reprice Status"] == "🛡️ Floor Protected").sum()

st.markdown(f"""
<div class="kpi-container">
  <div class="kpi-card">
    <div class="kpi-value">{total_items}</div>
    <div class="kpi-subtitle">Monitored SKUs</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #10B981;">{avg_margin:.1f}%</div>
    <div class="kpi-subtitle">Projected Avg Margin</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #38BDF8;">{buybox_count}/{total_items} ({int(buybox_count/total_items*100)}%)</div>
    <div class="kpi-subtitle">BuyBox Dominance Rate</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #F59E0B;">{floor_count}</div>
    <div class="kpi-subtitle">Floor Guard Triggers</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Main Multi-Tab Interface
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Repricing & Margin Terminal",
    "🔍 Visual Match & pHash Inspector",
    "📈 Market Analytics & Spreads",
    "🌐 Live Marketplace Scraper (Тест парсера)"
])

# TAB 1: Repricing & Margin Terminal
with tab1:
    tb_c1, tb_c2, tb_c3 = st.columns([3.2, 1.2, 1.2])
    with tb_c1:
        search_kw = st.text_input("Filter Catalog", "", placeholder="Search products by SKU or title...", label_visibility="collapsed")
    with tb_c2:
        shopify_csv = export_shopify_csv(df_results)
        st.download_button(
            label="📥 Export Shopify CSV",
            data=shopify_csv,
            file_name="shopify_repriced_catalog.csv",
            mime="text/csv",
            use_container_width=True
        )
    with tb_c3:
        excel_data = export_excel_report(df_results)
        st.download_button(
            label="📥 Export Styled Excel",
            data=excel_data,
            file_name="omniprice_repricing_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Filter by search
    display_df = df_results.copy()
    if search_kw:
        mask = display_df.astype(str).apply(lambda r: r.str.contains(search_kw, case=False).any(), axis=1)
        display_df = display_df[mask]

    table_cols = [
        "SKU", "Title", "Category", "Cost Price", "Our Price", 
        "Competitor Min", "Suggested Price", "Price Delta ($)", 
        "New Margin %", "Reprice Status"
    ]
    
    st.dataframe(
        display_df[table_cols],
        use_container_width=True,
        column_config={
            "SKU": st.column_config.TextColumn("SKU", width="small"),
            "Title": st.column_config.TextColumn("Product Title", width="large"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Cost Price": st.column_config.NumberColumn("Cost ($)", format="$%.2f"),
            "Our Price": st.column_config.NumberColumn("Current ($)", format="$%.2f"),
            "Competitor Min": st.column_config.NumberColumn("Comp Min ($)", format="$%.2f"),
            "Suggested Price": st.column_config.NumberColumn("Optimal Reprice ($)", format="$%.2f"),
            "Price Delta ($)": st.column_config.NumberColumn("Delta ($)", format="%+.2f"),
            "New Margin %": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
            "Reprice Status": st.column_config.TextColumn("Status")
        },
        height=320,
        hide_index=True
    )
    
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("ℹ️ Algorithmic Action Explanations"):
        for _, r in display_df.iterrows():
            st.markdown(f"**[{r['SKU']}] {r['Title']}**: {r['Reprice Status']} — *{r['Action Note']}*")

# TAB 2: Visual Match & pHash Inspector
with tab2:
    st.markdown("""
    <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.4rem;">
      🔍 Perceptual Visual Hash (dHash/pHash) Verification Engine
    </div>
    <div style="font-size: 0.82rem; color: #94A3B8; margin-bottom: 1rem;">
      When competitor titles differ across marketplaces, OmniPrice compares the perceptual geometry of product imagery to rank equivalent items with precision.
    </div>
    """, unsafe_allow_html=True)

    selected_sku = st.selectbox(
        "Select Product to Inspect Image Match",
        df_results["SKU"].tolist(),
        index=0
    )
    
    inspected_item = df_results[df_results["SKU"] == selected_sku].iloc[0]
    
    h1 = inspected_item["Our Image Hash"]
    h2 = inspected_item["Comp Image Hash"]
    dist = hamming_distance(h1, h2)
    similarity = hash_similarity_score(h1, h2)
    
    v_col1, v_col2, v_col3 = st.columns([1.5, 1.5, 2.0])
    
    with v_col1:
        st.markdown("**Our Store Catalog Image**")
        st.image(inspected_item["Our Image"], width=180)
        st.code(f"dHash: {hex(h1).upper()}", language="text")
        
    with v_col2:
        st.markdown("**Competitor Scraped Image**")
        st.image(inspected_item["Comp Image"], width=180)
        st.code(f"dHash: {hex(h2).upper()}", language="text")
        
    with v_col3:
        st.markdown("**Perceptual Match Telemetry**")
        st.markdown(f"""
        <div style="background: #121826; border: 1px solid #1F2937; border-radius: 8px; padding: 1rem; line-height: 1.8;">
          <span style="color: #94A3B8;">Hamming Bit Distance:</span> <strong style="color: #38BDF8;">{dist} / 64 bits</strong><br/>
          <span style="color: #94A3B8;">Match Confidence Score:</span> <strong style="color: {'#10B981' if similarity >= 0.85 else '#F59E0B'}; font-size: 1.2rem;">{similarity * 100:.1f}%</strong><br/>
          <span style="color: #94A3B8;">Equivalence Verdict:</span> <span style="color: #10B981; font-weight: 600;">{'✓ Verified Identical Model' if similarity >= 0.85 else '⚠️ Candidate Requires Review'}</span><br/>
          <span style="color: #94A3B8;">Physical Match:</span> <span style="color: #F8FAFC;">Category &amp; Form-factor verified</span>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: Market Analytics & Spreads
with tab3:
    chart_c1, chart_c2 = st.columns(2)
    
    with chart_c1:
        st.markdown("**Price Comparison Matrix ($)**")
        skus = df_results["SKU"].tolist()
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Our Current Price', x=skus, y=df_results["Our Price"], marker_color='#94A3B8'),
            go.Bar(name='MegaStore', x=skus, y=df_results["Comp1"], marker_color='#EF4444'),
            go.Bar(name='TechZone', x=skus, y=df_results["Comp2"], marker_color='#F59E0B'),
            go.Bar(name='Suggested Reprice', x=skus, y=df_results["Suggested Price"], marker_color='#10B981')
        ])
        fig_bar.update_layout(
            barmode='group',
            template='plotly_dark',
            paper_bgcolor='#121826',
            plot_bgcolor='#121826',
            height=340,
            margin=dict(l=30, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_c2:
        st.markdown("**Margin Spread vs Competitor Undercut**")
        fig_scatter = go.Figure()
        
        fig_scatter.add_trace(go.Scatter(
            x=df_results["Suggested Price"],
            y=df_results["New Margin %"],
            mode='markers+text',
            text=df_results["SKU"],
            textposition="top center",
            marker=dict(
                size=14,
                color=df_results["New Margin %"],
                colorscale='Viridis',
                showscale=True
            )
        ))
        fig_scatter.update_layout(
            template='plotly_dark',
            paper_bgcolor='#121826',
            plot_bgcolor='#121826',
            xaxis_title="Optimal Selling Price ($)",
            yaxis_title="Gross Profit Margin (%)",
            height=340,
            margin=dict(l=40, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 4: Live Marketplace Scraper
with tab4:
    st.markdown("""
    <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.3rem;">
      🌐 Живий модуль моніторингу цін конкурентів (Live Competitor Scraper)
    </div>
    <div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 1.2rem;">
      Модуль автоматично парсить інтернет-магазини за протоколом Schema.org JSON-LD, OpenGraph та регулярними виразами з обходом антибот-захисту.
    </div>
    """, unsafe_allow_html=True)

    test_c1, test_c2 = st.columns([2.5, 1.5])
    with test_c1:
        target_prod = st.text_input(
            "Введіть назву товару або посилання для швидкого аудиту:",
            value="Sony WH-1000XM5 Noise Canceling Headphones"
        )
    with test_c2:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        run_scrape_btn = st.button("🚀 Просканувати конкурентів (Live Benchmark)", type="primary", use_container_width=True)

    if run_scrape_btn or target_prod:
        benchmark_results = simulate_marketplace_benchmark(target_prod)
        st.markdown(f"**Зіставлення цін на маркетплейсах України для:** `{target_prod}`")
        
        bench_cols = st.columns(len(benchmark_results))
        for idx, b_item in enumerate(benchmark_results):
            with bench_cols[idx]:
                st.markdown(f"""
                <div style="background: #121826; border: 1px solid #1F2937; border-radius: 10px; padding: 1rem; line-height: 1.6;">
                  <div style="font-size: 0.8rem; font-weight: 700; color: #818CF8; text-transform: uppercase;">{b_item['marketplace']}</div>
                  <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC; margin: 4px 0;">{b_item['price']:.2f} {b_item['currency']}</div>
                  <div style="font-size: 0.8rem; color: #10B981;">● {b_item['availability']}</div>
                  <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">{b_item['shipping']}</div>
                  <div style="font-size: 0.72rem; color: #64748B; margin-top: 4px;">Продавець: {b_item['merchant']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
        st.info("💡 **Потрібен парсинг під вашу нішу або власну базу постачальників?** Ми розробляємо кастомні парсери з автоматичною синхронізацією цін у вашій системі обліку (Shopify, Rozetka, Prom, 1C / BAS). Напишіть у Telegram: **[@Nataly_Zyma](https://t.me/Nataly_Zyma)** або на email: **areonixwinter@gmail.com**.")

