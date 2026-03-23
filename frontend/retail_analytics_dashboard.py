"""
Retail Analytics Dashboard - Beige.AI
======================================
Admin interface for monitoring sales, inventory, and performance metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from pathlib import Path
import sys

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "scripts"))
from retail_database_manager import get_retail_database

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Beige.AI Retail Analytics",
    page_icon="📊",
    layout="wide"
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    .metric-box {
        background-color: #F5F3F0;
        border-left: 3px solid #BDB2A7;
        padding: 20px;
        border-radius: 2px;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #8B7D73;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-value {
        color: #2C2C2C;
        font-size: 28px;
        font-weight: 300;
        margin-top: 8px;
    }
    
    .low-stock {
        background-color: #FFF5E6;
        border-left: 3px solid #BDB2A7;
    }
    
    h1, h2 {
        color: #2C2C2C;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    hr {
        border: none;
        border-top: 1px solid #E5DDD6;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("Beige.AI Retail Analytics")
st.markdown("*Real-time sales, inventory, and performance monitoring*")

# Initialize database
retail_db = get_retail_database()

# ============================================================================
# SECTION 1: KEY METRICS
# ============================================================================

st.markdown("## 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

# Conversion Rate
with col1:
    conv_rate = retail_db.get_conversion_rate(days=7)
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Conversion Rate</div>
        <div class='metric-value'>{conv_rate:.1f}%</div>
        <div style='font-size: 12px; color: #8B7D73; margin-top: 5px;'>Recommended vs Purchased</div>
    </div>
    """, unsafe_allow_html=True)

# Total Sales
with col2:
    daily_sales = retail_db.get_daily_sales(days=1)
    total_sales_today = len(daily_sales) if not daily_sales.empty else 0
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Sales Today</div>
        <div class='metric-value'>{total_sales_today}</div>
        <div style='font-size: 12px; color: #8B7D73; margin-top: 5px;'>Items sold</div>
    </div>
    """, unsafe_allow_html=True)

# Total Revenue
with col3:
    revenue = retail_db.get_total_revenue(days=7)
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Revenue (7 Days)</div>
        <div class='metric-value'>${revenue:.2f}</div>
        <div style='font-size: 12px; color: #8B7D73; margin-top: 5px;'>Total sales</div>
    </div>
    """, unsafe_allow_html=True)

# Average Transaction
with col4:
    sales_history = retail_db.get_sales_history(days=7)
    avg_transaction = sales_history['price'].mean() if not sales_history.empty else 0
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Avg Transaction</div>
        <div class='metric-value'>${avg_transaction:.2f}</div>
        <div style='font-size: 12px; color: #8B7D73; margin-top: 5px;'>Per item</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SECTION 2: INVENTORY STATUS
# ============================================================================

st.markdown("## 📦 Inventory Status")

inventory_df = retail_db.get_inventory_status()
low_stock_df = retail_db.get_low_stock_items(threshold=10)

# Display inventory table
st.markdown("### Current Stock Levels")

if not inventory_df.empty:
    # Highlight low stock items
    def highlight_low_stock(row):
        if row['current_stock'] < 10:
            return ['background-color: #FFF5E6'] * len(row)
        return [''] * len(row)
    
    # Format for display
    display_df = inventory_df.copy()
    display_df['unit_price'] = display_df['unit_price'].apply(lambda x: f"${x:.2f}")
    display_df.columns = ['Cake', 'Stock', 'Price']
    
    # Show table
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )
    
    # Low stock alerts
    if not low_stock_df.empty:
        st.markdown("### ⚠️ Low Stock Alert")
        
        alert_cols = st.columns(len(low_stock_df))
        
        for idx, (_, row) in enumerate(low_stock_df.iterrows()):
            with alert_cols[idx]:
                st.markdown(f"""
                <div class='metric-box low-stock'>
                    <div class='metric-label'>Low Stock</div>
                    <div style='color: #2C2C2C; font-weight: 500; margin-top: 5px;'>{row['cake_name']}</div>
                    <div style='color: #8B7D73; font-size: 12px; margin-top: 5px;'>
                        {row['current_stock']} units remaining
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SECTION 3: TOP SELLING CAKES
# ============================================================================

st.markdown("## ⭐ Top Selling Cakes")

top_cakes = retail_db.get_top_selling_cakes(limit=8, days=30)

if not top_cakes.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create bar chart using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        
        colors = ['#BDB2A7' if i == 0 else '#D4CEC7' for i in range(len(top_cakes))]
        bars = ax.barh(top_cakes['cake'], top_cakes['units_sold'], color=colors)
        
        ax.set_xlabel('Units Sold', fontsize=11, color='#8B7D73')
        ax.set_title('Sales by Cake (30-Day)', fontsize=13, color='#2C2C2C', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.1, color='#BDB2A7')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.markdown("### Revenue by Cake")
        
        revenue_df = top_cakes[['cake', 'revenue']].copy()
        revenue_df.columns = ['Cake', 'Revenue']
        revenue_df['Revenue'] = revenue_df['Revenue'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(revenue_df, width="stretch", hide_index=True)

st.markdown("---")

# ============================================================================
# SECTION 4: MOOD-BASED SALES HEATMAP
# ============================================================================

st.markdown("## 🎭 Sales by Mood & Cake")

sales_by_mood = retail_db.get_sales_by_mood(days=30)

if not sales_by_mood.empty:
    # Create pivot table for heatmap
    pivot_data = sales_by_mood.pivot_table(
        values='count',
        index='mood',
        columns='bought_cake',
        fill_value=0
    )
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    
    im = ax.imshow(pivot_data.values, cmap='YlGnBu', aspect='auto')
    
    ax.set_xticks(np.arange(len(pivot_data.columns)))
    ax.set_yticks(np.arange(len(pivot_data.index)))
    ax.set_xticklabels(pivot_data.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(pivot_data.index, fontsize=10)
    
    # Add text annotations
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            value = pivot_data.values[i, j]
            if value > 0:
                text = ax.text(j, i, int(value), ha="center", va="center", color="white", fontsize=9)
    
    ax.set_title('Sales Heatmap: Mood × Cake Selection (30-Day)', fontsize=13, color='#2C2C2C', pad=15)
    ax.set_xlabel('Cake Selection', fontsize=11, color='#8B7D73')
    ax.set_ylabel('Customer Mood', fontsize=11, color='#8B7D73')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Also show table view
    st.markdown("### Details")
    
    detail_cols = st.columns(2)
    
    with detail_cols[0]:
        st.markdown("#### Most Popular Mood")
        mood_totals = sales_by_mood.groupby('mood')['count'].sum().sort_values(ascending=False)
        if not mood_totals.empty:
            st.markdown(f"**{mood_totals.index[0]}**  \n{mood_totals.values[0]} sales")
    
    with detail_cols[1]:
        st.markdown("#### Most Popular Cake")
        cake_totals = sales_by_mood.groupby('bought_cake')['count'].sum().sort_values(ascending=False)
        if not cake_totals.empty:
            st.markdown(f"**{cake_totals.index[0]}**  \n{cake_totals.values[0]} sales")

st.markdown("---")

# ============================================================================
# SECTION 5: DAILY SALES TREND
# ============================================================================

st.markdown("## 📅 Sales Trend (7-Day)")

daily_sales = retail_db.get_daily_sales(days=7)

if not daily_sales.empty:
    fig, ax = plt.subplots(figsize=(12, 4))
    
    ax.plot(daily_sales['date'], daily_sales['total_sales'], marker='o', color='#BDB2A7', linewidth=2, markersize=6)
    ax.fill_between(range(len(daily_sales)), daily_sales['total_sales'], alpha=0.2, color='#BDB2A7')
    
    ax.set_xlabel('Date', fontsize=11, color='#8B7D73')
    ax.set_ylabel('Sales Count', fontsize=11, color='#8B7D73')
    ax.set_title('Daily Sales Volume (7-Day)', fontsize=13, color='#2C2C2C', pad=15)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.1, color='#BDB2A7')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# ============================================================================
# SECTION 6: RECENT SALES
# ============================================================================

st.markdown("## 📋 Recent Sales")

recent_sales = retail_db.get_sales_history(days=7, limit=20)

if not recent_sales.empty:
    # Format for display
    display_sales = recent_sales.copy()
    display_sales['timestamp'] = display_sales['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    display_sales['price'] = display_sales['price'].apply(lambda x: f"${x:.2f}")
    display_sales['is_match'] = display_sales['is_match'].apply(lambda x: '✓' if x else '✗')
    
    display_sales = display_sales.rename(columns={
        'timestamp': 'Time',
        'recommended_cake': 'Recommended',
        'bought_cake': 'Purchased',
        'is_match': 'Match',
        'mood': 'Mood',
        'price': 'Price'
    })
    
    st.dataframe(
        display_sales[['Time', 'Recommended', 'Purchased', 'Match', 'Mood', 'Price']],
        width="stretch",
        hide_index=True
    )
else:
    st.info("No recent sales data available")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8B7D73; font-size: 12px; margin-top: 30px;'>
    <p>Beige.AI Retail Analytics • Real-time monitoring</p>
    <p>Data updates automatically • Last refresh: now</p>
</div>
""", unsafe_allow_html=True)
