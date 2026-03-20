"""
Checkout handler for Beige.AI retail operations.
Processes basket purchases and updates databases.
"""

import streamlit as st
from pathlib import Path
import sys

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "scripts"))
from retail_database_manager import get_retail_database


def process_checkout(basket, recommended_cake, mood, weather, db_analytics=None):
    """
    Process a complete checkout from basket.
    
    Args:
        basket: List of items from st.session_state.basket
        recommended_cake: Primary recommendation from AI
        mood: Customer mood
        weather: Weather condition
        db_analytics: Optional analytics database manager
    
    Returns:
        Tuple (success: bool, processed_count: int, total_revenue: float)
    """
    if not basket:
        st.warning("Your basket is empty. Add some cakes to proceed.")
        return False, 0, 0.0
    
    retail_db = get_retail_database()
    success_count = 0
    total_revenue = 0.0
    
    with st.spinner("Processing your purchase..."):
        for item in basket:
            purchased_cake = item['cake']
            price = item['price']
            is_recommended = item.get('recommended', False)
            
            # For recommended items, use the AI recommendation
            # For other items, treat as standalone purchases
            rec_cake = recommended_cake if is_recommended else purchased_cake
            
            try:
                # Process sale through retail database
                success, sale_id = retail_db.process_sale(
                    recommended_cake=rec_cake,
                    bought_cake=purchased_cake,
                    mood=mood,
                    weather=weather,
                    price=price
                )
                
                if success:
                    success_count += 1
                    total_revenue += price
                    print(f"✅ Sale #{sale_id}: {purchased_cake} for ${price:.2f}")
                else:
                    st.warning(f"⚠️ {purchased_cake} is out of stock.")
            
            except Exception as e:
                st.error(f"Error processing {purchased_cake}: {e}")
                print(f"Error: {e}")
    
    # Sales are already recorded through retail_db.process_sale() above
    # No additional analytics recording needed
    
    return success_count > 0, success_count, total_revenue


def show_checkout_confirmation(success_count: int, total_revenue: float):
    """Display checkout confirmation message."""
    if success_count == 0:
        st.error("❌ Could not complete your purchase. Please try again.")
        return
    
    st.success(f"✅ The ledger has been updated.")
    st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: #F5F3F0; border-left: 3px solid #BDB2A7; margin: 20px 0;'>
            <p style='font-size: 14px; color: #8B7D73; margin: 0;'>Items processed: <strong>{success_count}</strong></p>
            <p style='font-size: 14px; color: #8B7D73; margin: 5px 0;'>Total: <strong>${total_revenue:.2f}</strong></p>
            <p style='font-size: 16px; color: #2C2C2C; margin-top: 15px; font-style: italic;'>Enjoy your moment of solace.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #8B7D73; font-size: 14px; margin: 20px 0;'>
            Generate another recommendation above to continue browsing
        </div>
    """, unsafe_allow_html=True)
