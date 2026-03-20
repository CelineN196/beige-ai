"""
Backend scripts package for Beige AI.
Contains database management and utility functions.
"""

from .database_manager import DatabaseManager, get_database_manager

__all__ = ['DatabaseManager', 'get_database_manager']
