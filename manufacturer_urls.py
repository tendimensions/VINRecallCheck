"""
Mapping of vehicle manufacturers to their recall lookup URLs.
URLs are now loaded from manufacturer_urls.json file.
"""

import json
import os

def load_manufacturer_urls():
    """Load manufacturer URLs from JSON file."""
    json_file = 'manufacturer_urls.json'
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_recall_url(make: str) -> str:
    """
    Get the recall lookup URL for a specific manufacturer.
    
    Args:
        make: The vehicle manufacturer name
        
    Returns:
        The recall lookup URL, or NHTSA default if not found
    """
    manufacturer_urls = load_manufacturer_urls()
    make_upper = make.upper().strip()
    url = manufacturer_urls.get(make_upper)
    
    if url:
        return url
    else:
        # Default to NHTSA if manufacturer not found
        return 'https://www.nhtsa.gov/recalls'
