"""
Analytics Dashboard - Beige.AI Retail Intelligence System
==========================================================
Admin interface for monitoring recommendation performance and inventory.

Features:
- Conversion rate analytics
- Inventory status with low stock monitoring  
- Popularity trends by mood and weather
- Beige brand aesthetic (minimalist luxury styling)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add backend to path
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_BASE_DIR / "backend" / "scripts"))
sys.path.insert(0, str(_BASE_DIR / "backend"))

from database_manager import get_database_manager
from menu_config import CAKE_MENU


# ============================================================================
# BEIGE AESTHETIC STYLING
# ============================================================================

BEIGE_PALETTE = {
    'taupe': '#BDB2A7',
    'cream': '#F5F3F0',
    'dark_taupe': '#8B7D73',
    'gold': '#D4AF8F',
    'white': '#FFFFFF'
}


def render_dashboard():
    """
    Main analytics dashboard view with multiple metrics and visualizations.
    """
    st.set_page_config(
        page_title="Beige.AI Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS for beige aesthetic
    st.markdown("""
    <style>
        .metric-container {
            background-color: #F5F3F0;
            border-left: 3px solid #BDB2A7;
            padding: 20px;
            margin: 10px 0;
            border-radius: 2px;
        }
        
        .metric-label {
            color: #8B7D73;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .metric-value {
            color: #2C2C2C;
            font-size: 32px;
            font-weight: 300;
            margin-top: 10px;
        }
        
        .low-stock-alert {
            background-color: #F5F3F0;
            border-left: 3px solid #BDB2A7;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 2px;
        }
        
        .low-stock-label {
            color: #BDB2A7;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        hr {
            border: none;
            border-top: 1px solid #E5DDD6;
            margin: 20px 0;
        }
        
        h1, h2, h3 {
            color: #2C2C2C;
            font-weight: 300;
            letter-spacing: 2px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("## Performance Analytics")
    st.markdown("---")
    
    # Get database manager
    db = get_database_manager()
    
    # ===================================================================
    # SECTION 1: KEY METRICS
    # ===================================================================
    
    st.markdown("### 📈 Core Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    # Conversion Rate
    with col1:
        conversion_rate = db.get_conversion_rate(days=7)
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">7-Day Conversion Rate</div>
            <div class="metric-value">{conversion_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendation Accuracy
    with col2:
        accuracy = db.get_recommendation_accuracy(days=7)
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Recommendation Accuracy</div>
            <div class="metric-value">{accuracy:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Inventory Status
    with col3:
        inventory_stats = db.get_total_inventory_value()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Items in Inventory</div>
            <div class="metric-value">{inventory_stats['total_items']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===================================================================
    # SECTION 2: INVENTORY STATUS
    # ===================================================================
    
    st.markdown("### 📦 Inventory Status")
    
    low_stock_items = db.get_low_stock_items()
    
    if low_stock_items:
        st.markdown(
            f"<div style='color: #8B7D73; font-size: 14px; margin-bottom: 16px;'>"
            f"{len(low_stock_items)} item(s) below reorder level</div>",
            unsafe_allow_html=True
        )
        
        for item in low_stock_items:
            cake_name = item['cake_name']
            stock = item['stock']
            reorder = item['reorder_level']
            
            # Visual indicator
            pct_full = min(100, (stock / reorder) * 100) if reorder > 0 else 0
            
            st.markdown(f"""
            <div class="low-stock-alert">
                <div class="low-stock-label">Low Stock</div>
                <div style='color: #2C2C2C; margin-top: 6px; font-weight: 500;'>
                    {cake_name}
                </div>
                <div style='color: #8B7D73; font-size: 12px; margin-top: 4px;'>
                    Stock: {stock} / Reorder at: {reorder}
                </div>
                <div style='background-color: #EFE7DE; height: 2px; margin-top: 8px; border-radius: 1px;'>
                    <div style='background-color: #BDB2A7; height: 100%; width: {pct_full}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='color: #8B7D73; padding: 20px; text-align: center;'>"
            "✓ All items adequately stocked</div>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # ===================================================================
    # SECTION 3: POPULARITY TRENDS
    # ===================================================================
    
    st.markdown("### ✨ Popularity Trends")
    
    popularity_df = db.get_popularity_by_context(limit=15)
    
    if not popularity_df.empty:
        # Display as a clean table
        display_df = popularity_df.copy()
        display_df.columns = ['Mood', 'Weather', 'Cake Selected', 'Purchases']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Purchases': st.column_config.ProgressColumn(
                    'Purchases',
                    min_value=0,
                    max_value=display_df['Purchases'].max()
                )
            }
        )
        
        # Chart: Most popular cakes overall
        top_cakes = popularity_df.groupby('selected_cake')['purchase_count'].sum().sort_values(ascending=False).head(8)
        
        if len(top_cakes) > 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Beige aesthetic colors
            colors = ['#BDB2A7' if i == 0 else '#E5DDD6' for i in range(len(top_cakes))]
            
            ax.barh(range(len(top_cakes)), top_cakes.values, color=colors, edgecolor='#F5F3F0')
            ax.set_yticks(range(len(top_cakes)))
            ax.set_yticklabels(top_cakes.index, fontsize=10)
            ax.set_xlabel('Purchases', fontsize=10, color='#8B7D73')
            ax.set_title('Most Popular Cakes', fontsize=12, color='#2C2C2C', pad=20)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E5DDD6')
            ax.spines['bottom'].set_color('#E5DDD6')
            ax.grid(axis='x', alpha=0.1, color='#BDB2A7')
            
            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.markdown(
            "<div style='color: #8B7D73; padding: 20px; text-align: center;'>"
            "No purchase data available yet</div>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # ===================================================================
    # SECTION 4: TIME SERIES ANALYSIS
    # ===================================================================
    
    st.markdown("### 📅 Daily Performance")
    
    purchase_history_df = db.get_purchase_history_dataframe(days=30)
    
    if not purchase_history_df.empty:
        # Daily conversion chart
        purchase_history_df['date'] = purchase_history_df['timestamp'].dt.date
        daily_stats = purchase_history_df.groupby('date').agg({
            'id': 'count',
            'is_conversion': 'sum'
        }).rename(columns={'id': 'recommendations', 'is_conversion': 'conversions'})
        daily_stats['conversion_rate'] = (daily_stats['conversions'] / daily_stats['recommendations'] * 100).round(1)
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(daily_stats.index, daily_stats['conversion_rate'], 
                color='#BDB2A7', linewidth=2, marker='o', markersize=4)
        ax.fill_between(range(len(daily_stats)), daily_stats['conversion_rate'], 
                        alpha=0.2, color='#BDB2A7')
        
        ax.set_ylabel('Conversion Rate (%)', fontsize=10, color='#8B7D73')
        ax.set_xlabel('Date', fontsize=10, color='#8B7D73')
        ax.set_title('Daily Conversion Rate (Last 30 Days)', fontsize=12, color='#2C2C2C', pad=20)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5DDD6')
        ax.spines['bottom'].set_color('#E5DDD6')
        ax.grid(alpha=0.1, color='#BDB2A7')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y)}%'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # ===================================================================
    # SECTION 5: DATA EXPORT
    # ===================================================================
    
    st.markdown("### 📥 Data Export")
    
    if purchase_history_df.empty:
        st.markdown(
            "<div style='color: #8B7D73;'>No purchase history available for export</div>",
            unsafe_allow_html=True
        )
    else:
        # Export buttons
        csv = purchase_history_df.to_csv(index=False)
        st.download_button(
            label="Download Purchase History (CSV)",
            data=csv,
            file_name=f"beige_ai_purchase_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def show_admin_panel(show_analytics: bool = False) -> bool:
    """
    Show admin panel toggle in sidebar.
    Returns True if analytics dashboard should be shown.
    
    Args:
        show_analytics: Current admin mode state
    
    Returns:
        New admin mode state
    """
    st.sidebar.markdown("---")
    admin_mode = st.sidebar.toggle("🔐 Admin Mode", value=show_analytics)
    
    if admin_mode:
        st.sidebar.markdown("##### Admin Controls")
        
        # Initialize inventory from menu if needed
        if st.sidebar.button("Initialize Inventory from Menu"):
            db = get_database_manager()
            db.initialize_inventory(
                CAKE_MENU,  # CAKE_MENU is a list
                initial_stock=20,
                reorder_level=5
            )
            st.sidebar.success("✓ Inventory initialized")
    
    return admin_mode


# ============================================================================
# MAIN ENTRY POINT FOR STANDALONE DASHBOARD
# ============================================================================

if __name__ == "__main__":
    render_dashboard()
