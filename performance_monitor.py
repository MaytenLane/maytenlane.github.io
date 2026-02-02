#!/usr/bin/env python3
"""
==============================================================================
PERFORMANCE MONITORING SCRIPT FOR MAYTEN LANE WEBSITE
Automated Core Web Vitals and performance metrics tracking
==============================================================================

This script monitors website performance using Google PageSpeed Insights API
and provides actionable insights for optimization.
"""

import requests
import aiohttp
import asyncio
import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import os

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================
WEBSITE_URL = "https://www.maytenlane.com"
OUTPUT_FILE = "performance_metrics.csv"

# =============================================================================
# PERFORMANCE THRESHOLDS
# Core Web Vitals and performance targets
# =============================================================================
PERFORMANCE_THRESHOLDS = {
    "first_contentful_paint": 1.5,      # seconds
    "largest_contentful_paint": 2.5,    # seconds
    "cumulative_layout_shift": 0.1,     # score
    "time_to_interactive": 3.8,         # seconds
    "speed_index": 3.4,                 # seconds
    "total_blocking_time": 300          # milliseconds
}

# Recommendations for performance issues
RECOMMENDATION_MAP = {
    "first_contentful_paint": "Optimize critical rendering path",
    "largest_contentful_paint": "Optimize image loading and rendering",
    "cumulative_layout_shift": "Fix layout shifts and use proper image dimensions",
    "time_to_interactive": "Reduce JavaScript execution time"
}

# Shared empty dictionary to avoid repeated allocations
EMPTY_DICT = {}

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================
def load_api_key() -> str:
    """
    Load Google PageSpeed API key from environment or config file.
    
    Returns:
        API key string or empty string if not found
    """
    api_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    if not api_key:
        config_file = Path('.pagespeed_config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key')
            except (json.JSONDecodeError, IOError):
                pass
    
    return api_key

# =============================================================================
# API COMMUNICATION
# =============================================================================
def test_page_speed(url: str, api_key: str, strategy: str = "mobile") -> Dict[str, Any]:
    """
    Test page speed using Google PageSpeed Insights API.
    
    Args:
        url: Website URL to test
        api_key: Google PageSpeed API key
        strategy: Testing strategy ('mobile' or 'desktop')
        
    Returns:
        Dict containing API response or error information
    """
    if not api_key:
        return {"error": "No API key provided"}
    
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy,
        "category": "performance",
        "utm_source": "maytenlane-performance-monitor"
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}


async def test_page_speed_async(session: aiohttp.ClientSession, url: str, api_key: str, strategy: str = "mobile") -> Dict[str, Any]:
    """
    Test page speed using Google PageSpeed Insights API asynchronously.

    Args:
        session: aiohttp ClientSession
        url: Website URL to test
        api_key: Google PageSpeed API key
        strategy: Testing strategy ('mobile' or 'desktop')

    Returns:
        Dict containing API response or error information
    """
    if not api_key:
        return {"error": "No API key provided"}

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy,
        "category": "performance",
        "utm_source": "maytenlane-performance-monitor"
    }

    try:
        timeout_settings = aiohttp.ClientTimeout(total=30)
        async with session.get(api_url, params=params, timeout=timeout_settings) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        return {"error": f"API request failed: {e}"}
    except asyncio.TimeoutError:
        return {"error": "API request timed out"}

# =============================================================================
# DATA EXTRACTION AND PROCESSING
# =============================================================================
def extract_core_web_vitals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Core Web Vitals from PageSpeed Insights data.
    
    Args:
        data: Raw API response data
        
    Returns:
        Dict containing extracted performance metrics
    """
    if "error" in data:
        return data
    
    try:
        lighthouse_result = data.get("lighthouseResult", EMPTY_DICT)
        audits = lighthouse_result.get("audits", EMPTY_DICT)
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "url": data.get("id", ""),
            "strategy": lighthouse_result.get("configSettings", EMPTY_DICT).get("formFactor", ""),
            "performance_score": lighthouse_result.get("categories", EMPTY_DICT).get("performance", EMPTY_DICT).get("score", 0) * 100,
            "first_contentful_paint": audits.get("first-contentful-paint", EMPTY_DICT).get("numericValue", 0) / 1000,
            "largest_contentful_paint": audits.get("largest-contentful-paint", EMPTY_DICT).get("numericValue", 0) / 1000,
            "cumulative_layout_shift": audits.get("cumulative-layout-shift", EMPTY_DICT).get("numericValue", 0),
            "time_to_interactive": audits.get("interactive", EMPTY_DICT).get("numericValue", 0) / 1000,
            "speed_index": audits.get("speed-index", EMPTY_DICT).get("numericValue", 0) / 1000,
            "total_blocking_time": audits.get("total-blocking-time", EMPTY_DICT).get("numericValue", 0),
            "first_meaningful_paint": audits.get("first-meaningful-paint", EMPTY_DICT).get("numericValue", 0) / 1000,
            "max_potential_fid": audits.get("max-potential-fid", EMPTY_DICT).get("numericValue", 0)
        }
        
        return metrics
    except Exception as e:
        return {"error": f"Failed to extract metrics: {e}"}

def analyze_performance(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze performance metrics against defined thresholds.
    
    Args:
        metrics: Performance metrics dictionary
        thresholds: Dictionary of performance thresholds
        
    Returns:
        Dict containing analysis results and recommendations
    """
    if "error" in metrics:
        return metrics
    
    analysis = {
        "timestamp": metrics["timestamp"],
        "url": metrics["url"],
        "overall_score": "PASS",
        "issues": [],
        "recommendations": []
    }
    
    # Check each metric against thresholds
    for metric, threshold in thresholds.items():
        if metric in metrics:
            value = metrics[metric]
            if value > threshold:
                analysis["overall_score"] = "FAIL"
                analysis["issues"].append(f"{metric}: {value:.2f} (threshold: {threshold})")
                
                # Provide specific recommendations
                if metric in RECOMMENDATION_MAP:
                    analysis["recommendations"].append(RECOMMENDATION_MAP[metric])
    
    return analysis

# =============================================================================
# DATA PERSISTENCE
# =============================================================================
def save_metrics_to_csv(metrics: List[Dict[str, Any]], filename: str):
    """
    Save performance metrics to CSV file for historical tracking.
    
    Args:
        metrics: List of performance metrics dictionaries
        filename: Output CSV filename
    """
    if not metrics:
        return
    
    fieldnames = metrics[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)

# =============================================================================
# REPORTING AND OUTPUT
# =============================================================================
def generate_performance_report(analysis: Dict[str, Any]) -> str:
    """
    Generate a human-readable performance report.
    
    Args:
        analysis: Performance analysis results
        
    Returns:
        Formatted report string
    """
    if "error" in analysis:
        return f"Error: {analysis['error']}"
    
    report_parts = []
    report_parts.append(f"""
PERFORMANCE REPORT FOR {analysis['url']}
Generated: {analysis['timestamp']}
Overall Score: {analysis['overall_score']}

""")
    
    if analysis["issues"]:
        report_parts.append("ISSUES FOUND:\n")
        for issue in analysis["issues"]:
            report_parts.append(f"  • {issue}\n")
        report_parts.append("\n")
    
    if analysis["recommendations"]:
        report_parts.append("RECOMMENDATIONS:\n")
        for rec in analysis["recommendations"]:
            report_parts.append(f"  • {rec}\n")
        report_parts.append("\n")
    
    return "".join(report_parts)

# =============================================================================
# MAIN EXECUTION
# =============================================================================
async def run_strategy_test(
    session: aiohttp.ClientSession,
    url: str,
    api_key: str,
    strategy: str
) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Run a single strategy test asynchronously and process results.
    """
    print(f"\n📱 Starting {strategy} performance test...")

    # Test page speed
    result = await test_page_speed_async(session, url, api_key, strategy)
    if "error" in result:
        print(f"✗ Error testing {strategy}: {result['error']}")
        return None
    
    # Extract metrics
    metrics = extract_core_web_vitals(result)
    if "error" in metrics:
        print(f"✗ Error extracting metrics for {strategy}: {metrics['error']}")
        return None

    # Analyze performance
    analysis = analyze_performance(metrics, PERFORMANCE_THRESHOLDS)

    # Display results
    score = analysis.get('overall_score', 'N/A')
    issues_count = len(analysis.get('issues', []))

    print(f"📱 {strategy.capitalize()} Results:")
    print(f"  Performance Score: {score}")
    if issues_count > 0:
        print(f"  Issues Found: {issues_count}")
    else:
        print("  ✓ All metrics within thresholds")

    return metrics, analysis

async def async_main():
    """
    Async main function to run performance monitoring.
    """
    print("=" * 70)
    print("PERFORMANCE MONITORING FOR MAYTEN LANE WEBSITE")
    print("=" * 70)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("WARNING: No Google PageSpeed API key found")
        print("\nPlease set the following environment variable:")
        print("  GOOGLE_PAGESPEED_API_KEY")
        print("\nOr create a .pagespeed_config.json file")
        return
    
    # Test both mobile and desktop strategies
    strategies = ["mobile", "desktop"]
    
    print(f"\nTesting website: {WEBSITE_URL}")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        tasks = [run_strategy_test(session, WEBSITE_URL, api_key, strategy) for strategy in strategies]
        results = await asyncio.gather(*tasks)

    # Filter out None results
    valid_results = [r for r in results if r is not None]
    
    # Save metrics to CSV
    all_metrics = [r[0] for r in valid_results]
    if all_metrics:
        save_metrics_to_csv(all_metrics, OUTPUT_FILE)
        print(f"\n💾 Metrics saved to {OUTPUT_FILE}")
    
    # Generate and display final report
    if valid_results:
        print("\n" + "=" * 70)
        print("FINAL PERFORMANCE REPORT")
        print("=" * 70)
        
        for metrics, analysis in valid_results:
            strategy = metrics.get('strategy', 'unknown')

            print(f"\n{strategy.upper()} ANALYSIS:")
            print(generate_performance_report(analysis))
    
    print("\n" + "=" * 70)
    print("Performance monitoring complete!")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
