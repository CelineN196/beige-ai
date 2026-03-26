# Services module
# Business logic and service functions

from services.checkout_handler import process_checkout, show_checkout_confirmation
from services.beige_ai_copywriter import generate_luxury_description

__all__ = [
    "process_checkout",
    "show_checkout_confirmation",
    "generate_luxury_description",
]
