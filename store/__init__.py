# fetch_store/__init__.py

# Exposing key modules for easier imports
from .store_jobs import *
# from .test_firestore import *

# Utility functions for storing jobs
def store_all_jobs():
    """Function to store all fetched jobs into Firestore."""
    print("Storing jobs... (implement logic here)")

__all__ = ["fetch_jobs", "store_jobs", "store_all_jobs"]