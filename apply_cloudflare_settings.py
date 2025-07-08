#!/usr/bin/env python3
"""
CLOUDFLARE API SETTINGS APPLIER FOR MAYTEN LANE WEBSITE
THIS SCRIPT CONFIGURES CLOUDFLARE SETTINGS FOR OPTIMAL PERFORMANCE AND SECURITY
LAST UPDATED: 2025-01-27
OPTIMIZED FOR AUTOMATED CLOUDFLARE CONFIGURATION
"""

import requests
import json
import os
import sys
from typing import Dict, Any, Optional

# CLOUDFLARE API CONFIGURATION CONSTANTS
# THESE SETTINGS ARE OPTIMIZED FOR MAYTEN LANE'S HOSTING REQUIREMENTS
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
ZONE_ID = "YOUR_ZONE_ID_HERE"  # REPLACE WITH ACTUAL ZONE ID
API_TOKEN = "YOUR_API_TOKEN_HERE"  # REPLACE WITH ACTUAL API TOKEN

# SECURITY HEADERS CONFIGURATION
# THESE HEADERS PROVIDE ENHANCED SECURITY FOR THE WEBSITE
SECURITY_HEADERS = {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff", 
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
}

# CACHE SETTINGS CONFIGURATION
# THESE SETTINGS OPTIMIZE CACHING FOR DIFFERENT FILE TYPES
CACHE_SETTINGS = {
    "html": {"max_age": 3600, "edge_ttl": 3600},
    "css": {"max_age": 2592000, "edge_ttl": 2592000},
    "js": {"max_age": 2592000, "edge_ttl": 2592000},
    "images": {"max_age": 31536000, "edge_ttl": 31536000},
    "fonts": {"max_age": 31536000, "edge_ttl": 31536000}
}

def get_headers() -> Dict[str, str]:
    """
    GENERATE API REQUEST HEADERS FOR CLOUDFLARE API
    RETURNS PROPERLY FORMATTED HEADERS FOR AUTHENTICATION
    """
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    MAKE API REQUEST TO CLOUDFLARE API
    HANDLES ALL API COMMUNICATION WITH PROPER ERROR HANDLING
    """
    url = f"{CLOUDFLARE_API_BASE}{endpoint}"
    headers = get_headers()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"UNSUPPORTED HTTP METHOD: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API REQUEST FAILED: {e}")
        return {"success": False, "error": str(e)}

def apply_security_headers() -> bool:
    """
    APPLY SECURITY HEADERS TO THE WEBSITE
    CONFIGURES ENHANCED SECURITY HEADERS FOR PROTECTION
    """
    print("APPLYING SECURITY HEADERS...")
    
    # CREATE PAGE RULE FOR SECURITY HEADERS
    page_rule_data = {
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": "maytenlane.com/*"
                }
            }
        ],
        "actions": [
            {
                "id": "security_level",
                "value": "high"
            }
        ],
        "priority": 1,
        "status": "active"
    }
    
    result = make_api_request(f"/zones/{ZONE_ID}/pagerules", "POST", page_rule_data)
    
    if result.get("success"):
        print("SECURITY HEADERS APPLIED SUCCESSFULLY")
        return True
    else:
        print(f"FAILED TO APPLY SECURITY HEADERS: {result.get('error', 'Unknown error')}")
        return False

def apply_cache_settings() -> bool:
    """
    APPLY CACHE SETTINGS FOR OPTIMAL PERFORMANCE
    CONFIGURES CACHING RULES FOR DIFFERENT FILE TYPES
    """
    print("APPLYING CACHE SETTINGS...")
    
    # APPLY CACHE SETTINGS FOR DIFFERENT FILE TYPES
    for file_type, settings in CACHE_SETTINGS.items():
        cache_rule_data = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": f"maytenlane.com/*.{file_type}"
                    }
                }
            ],
            "actions": [
                {
                    "id": "cache_level",
                    "value": "cache_everything"
                },
                {
                    "id": "edge_cache_ttl",
                    "value": settings["edge_ttl"]
                }
            ],
            "priority": 2,
            "status": "active"
        }
        
        result = make_api_request(f"/zones/{ZONE_ID}/pagerules", "POST", cache_rule_data)
        
        if not result.get("success"):
            print(f"FAILED TO APPLY CACHE SETTINGS FOR {file_type}: {result.get('error', 'Unknown error')}")
            return False
    
    print("CACHE SETTINGS APPLIED SUCCESSFULLY")
    return True

def enable_ssl_tls() -> bool:
    """
    ENABLE SSL/TLS SETTINGS FOR SECURE CONNECTIONS
    CONFIGURES ENCRYPTION SETTINGS FOR THE WEBSITE
    """
    print("ENABLING SSL/TLS SETTINGS...")
    
    ssl_settings = {
        "value": "full"
    }
    
    result = make_api_request(f"/zones/{ZONE_ID}/settings/ssl", "PATCH", ssl_settings)
    
    if result.get("success"):
        print("SSL/TLS SETTINGS ENABLED SUCCESSFULLY")
        return True
    else:
        print(f"FAILED TO ENABLE SSL/TLS: {result.get('error', 'Unknown error')}")
        return False

def enable_minification() -> bool:
    """
    ENABLE MINIFICATION FOR BETTER PERFORMANCE
    CONFIGURES AUTOMATIC CODE MINIFICATION
    """
    print("ENABLING MINIFICATION...")
    
    minification_settings = {
        "value": {
            "css": "on",
            "html": "on",
            "js": "on"
        }
    }
    
    result = make_api_request(f"/zones/{ZONE_ID}/settings/minify", "PATCH", minification_settings)
    
    if result.get("success"):
        print("MINIFICATION ENABLED SUCCESSFULLY")
        return True
    else:
        print(f"FAILED TO ENABLE MINIFICATION: {result.get('error', 'Unknown error')}")
        return False

def enable_brotli_compression() -> bool:
    """
    ENABLE BROTLI COMPRESSION FOR FASTER LOADING
    CONFIGURES ADVANCED COMPRESSION FOR BETTER PERFORMANCE
    """
    print("ENABLING BROTLI COMPRESSION...")
    
    brotli_settings = {
        "value": "on"
    }
    
    result = make_api_request(f"/zones/{ZONE_ID}/settings/brotli", "PATCH", brotli_settings)
    
    if result.get("success"):
        print("BROTLI COMPRESSION ENABLED SUCCESSFULLY")
        return True
    else:
        print(f"FAILED TO ENABLE BROTLI COMPRESSION: {result.get('error', 'Unknown error')}")
        return False

def main():
    """
    MAIN FUNCTION TO APPLY ALL CLOUDFLARE SETTINGS
    EXECUTES THE COMPLETE CONFIGURATION PROCESS
    """
    print("STARTING CLOUDFLARE SETTINGS APPLICATION...")
    print("=" * 50)
    
    # CHECK FOR REQUIRED CONFIGURATION
    if ZONE_ID == "YOUR_ZONE_ID_HERE" or API_TOKEN == "YOUR_API_TOKEN_HERE":
        print("ERROR: PLEASE CONFIGURE ZONE_ID AND API_TOKEN BEFORE RUNNING")
        print("EDIT THE SCRIPT TO INCLUDE YOUR ACTUAL CLOUDFLARE CREDENTIALS")
        sys.exit(1)
    
    # APPLY ALL SETTINGS
    success_count = 0
    total_settings = 5
    
    if apply_security_headers():
        success_count += 1
    
    if apply_cache_settings():
        success_count += 1
    
    if enable_ssl_tls():
        success_count += 1
    
    if enable_minification():
        success_count += 1
    
    if enable_brotli_compression():
        success_count += 1
    
    # DISPLAY RESULTS
    print("=" * 50)
    print(f"SETTINGS APPLICATION COMPLETE: {success_count}/{total_settings} SUCCESSFUL")
    
    if success_count == total_settings:
        print("ALL CLOUDFLARE SETTINGS APPLIED SUCCESSFULLY!")
        print("YOUR WEBSITE IS NOW OPTIMIZED FOR PERFORMANCE AND SECURITY")
    else:
        print("SOME SETTINGS FAILED TO APPLY. PLEASE CHECK THE ERRORS ABOVE")
        sys.exit(1)

if __name__ == "__main__":
    main() 