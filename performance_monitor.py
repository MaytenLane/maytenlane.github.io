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
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
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
        lighthouse_result = data.get("lighthouseResult", {})
        audits = lighthouse_result.get("audits", {})
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "url": data.get("id", ""),
            "strategy": lighthouse_result.get("configSettings", {}).get("formFactor", ""),
            "performance_score": lighthouse_result.get("categories", {}).get("performance", {}).get("score", 0) * 100,
            "first_contentful_paint": audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000,
            "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
            "cumulative_layout_shift": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
            "time_to_interactive": audits.get("interactive", {}).get("numericValue", 0) / 1000,
            "speed_index": audits.get("speed-index", {}).get("numericValue", 0) / 1000,
            "total_blocking_time": audits.get("total-blocking-time", {}).get("numericValue", 0),
            "first_meaningful_paint": audits.get("first-meaningful-paint", {}).get("numericValue", 0) / 1000,
            "max_potential_fid": audits.get("max-potential-fid", {}).get("numericValue", 0)
        }
        
        return metrics
    except Exception as e:
        return {"error": f"Failed to extract metrics: {e}"}

def analyze_performance(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze performance metrics against defined thresholds.
    
    Args:
        metrics: Performance metrics dictionary
        
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
    for metric, threshold in PERFORMANCE_THRESHOLDS.items():
        if metric in metrics:
            value = metrics[metric]
            if value > threshold:
                analysis["overall_score"] = "FAIL"
                analysis["issues"].append(f"{metric}: {value:.2f} (threshold: {threshold})")
                
                # Provide specific recommendations
                if metric == "first_contentful_paint":
                    analysis["recommendations"].append("Optimize critical rendering path")
                elif metric == "largest_contentful_paint":
                    analysis["recommendations"].append("Optimize image loading and rendering")
                elif metric == "cumulative_layout_shift":
                    analysis["recommendations"].append("Fix layout shifts and use proper image dimensions")
                elif metric == "time_to_interactive":
                    analysis["recommendations"].append("Reduce JavaScript execution time")
    
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
    
    report = f"""
PERFORMANCE REPORT FOR {analysis['url']}
Generated: {analysis['timestamp']}
Overall Score: {analysis['overall_score']}

"""
    
    if analysis["issues"]:
        report += "ISSUES FOUND:\n"
        for issue in analysis["issues"]:
            report += f"  • {issue}\n"
        report += "\n"
    
    if analysis["recommendations"]:
        report += "RECOMMENDATIONS:\n"
        for rec in analysis["recommendations"]:
            report += f"  • {rec}\n"
        report += "\n"
    
    return report

# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    """
    Main function to run performance monitoring.
    
    Executes comprehensive performance testing for both mobile and desktop
    strategies and generates detailed reports.
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
    all_metrics = []
    
    print(f"\nTesting website: {WEBSITE_URL}")
    print("-" * 50)
    
    for strategy in strategies:
        print(f"\n📱 Testing {strategy} performance...")
        
        # Test page speed
        result = test_page_speed(WEBSITE_URL, api_key, strategy)
        if "error" in result:
            print(f"✗ Error testing {strategy}: {result['error']}")
            continue
        
        # Extract metrics
        metrics = extract_core_web_vitals(result)
        if "error" in metrics:
            print(f"✗ Error extracting metrics for {strategy}: {metrics['error']}")
            continue
        
        # Analyze performance
        analysis = analyze_performance(metrics)
        
        # Display results
        score = analysis.get('overall_score', 'N/A')
        issues_count = len(analysis.get('issues', []))
        
        print(f"  Performance Score: {score}")
        if issues_count > 0:
            print(f"  Issues Found: {issues_count}")
        else:
            print("  ✓ All metrics within thresholds")
        
        all_metrics.append(metrics)
    
    # Save metrics to CSV
    if all_metrics:
        save_metrics_to_csv(all_metrics, OUTPUT_FILE)
        print(f"\n💾 Metrics saved to {OUTPUT_FILE}")
    
    # Generate and display final report
    if all_metrics:
        print("\n" + "=" * 70)
        print("FINAL PERFORMANCE REPORT")
        print("=" * 70)
        
        for i, metrics in enumerate(all_metrics):
            analysis = analyze_performance(metrics)
            strategy = strategies[i] if i < len(strategies) else "unknown"
            print(f"\n{strategy.upper()} ANALYSIS:")
            print(generate_performance_report(analysis))
    
    print("\n" + "=" * 70)
    print("Performance monitoring complete!")

if __name__ == "__main__":
    main()
