"""
apply_cloudflare_settings.py

This script documents and (optionally) applies recommended Cloudflare settings for optimal SEO, security, and performance for a static website.

- Requires: python-requests
- Usage: Fill in your Cloudflare API credentials and zone ID, then run the script.
- If credentials are not provided, the script will output recommended settings for manual application.
"""

import os
import requests

# --- User Configuration ---
CLOUDFLARE_API_TOKEN = os.getenv('CF_API_TOKEN', '')  # Or paste your token here
ZONE_ID = os.getenv('CF_ZONE_ID', '')                # Or paste your zone ID here
HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

# --- Recommended Cloudflare Settings ---
RECOMMENDED_SETTINGS = [
    ("Always Use HTTPS", "always_use_https", True),
    ("Automatic HTTPS Rewrites", "automatic_https_rewrites", True),
    ("SSL/TLS Mode", "ssl", "full"),
    ("HSTS", "hsts", {
        "enabled": True,
        "max_age": 31536000,
        "include_subdomains": True,
        "preload": True
    }),
    ("Brotli Compression", "brotli", True),
    ("Auto Minify CSS", "minify", {"css": True}),
    ("Auto Minify JS", "minify", {"js": True}),
    ("Auto Minify HTML", "minify", {"html": True}),
    ("Cache Level", "cache_level", "aggressive"),
    ("Edge Cache TTL", "edge_cache_ttl", 31536000),
    ("Rocket Loader", "rocket_loader", False),
    ("Polish Images", "polish", "lossless"),
    ("Mirage", "mirage", True),
    ("Security Level", "security_level", "high"),
    ("Browser Cache TTL", "browser_cache_ttl", 31536000),
    ("Email Obfuscation", "email_obfuscation", True),
    ("Hotlink Protection", "hotlink_protection", True),
]

# --- Helper Functions ---
def print_recommendations():
    print("\nRecommended Cloudflare Settings for Static Sites:\n")
    for label, key, value in RECOMMENDED_SETTINGS:
        print(f"- {label}: {value}")
    print("\nApply these in the Cloudflare dashboard for best SEO, security, and performance.")

def apply_settings():
    if not CLOUDFLARE_API_TOKEN or not ZONE_ID:
        print("\n[!] Cloudflare API token or zone ID not set. Skipping API calls.\n")
        print_recommendations()
        return
    print("\nApplying recommended settings via Cloudflare API...\n")
    for label, key, value in RECOMMENDED_SETTINGS:
        url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/{key}"
        payload = {"value": value}
        try:
            resp = requests.patch(url, headers=HEADERS, json=payload)
            if resp.ok:
                print(f"[✓] {label} set to {value}")
            else:
                print(f"[!] Failed to set {label}: {resp.text}")
        except Exception as e:
            print(f"[!] Error setting {label}: {e}")

if __name__ == "__main__":
    apply_settings() 