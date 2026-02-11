#!/usr/bin/env python3
"""
PERFORMANCE MONITORING SCRIPT FOR MAYTEN LANE WEBSITE
Automated Core Web Vitals and performance metrics tracking

This script monitors website performance using Google PageSpeed Insights API
and provides actionable insights for optimization.
"""

import aiohttp
import asyncio
import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import functools
from pathlib import Path
import os

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

# Configuration Constants
WEBSITE_URL = "https://www.maytenlane.com"
OUTPUT_FILE = "performance_metrics.csv"

# Performance Thresholds
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
    "cumulative_layout_shift":
        "Fix layout shifts and use proper image dimensions",
    "time_to_interactive": "Reduce JavaScript execution time"
}

# Metric mapping: (internal_key, audit_key, divisor)
# Defined as a module-level constant to avoid repeated allocation
METRIC_MAP = (
    ("first_contentful_paint", "first-contentful-paint", 1000),
    ("largest_contentful_paint", "largest-contentful-paint", 1000),
    ("cumulative_layout_shift", "cumulative-layout-shift", 1),
    ("time_to_interactive", "interactive", 1000),
    ("speed_index", "speed-index", 1000),
    ("total_blocking_time", "total-blocking-time", 1),
    ("first_meaningful_paint", "first-meaningful-paint", 1000),
    ("max_potential_fid", "max-potential-fid", 1),
)

# Shared empty dictionary to avoid repeated allocations
EMPTY_DICT = {}

# API Timeout setting to avoid repeated instantiation
API_TIMEOUT = aiohttp.ClientTimeout(total=30)

# Configuration Management


def _load_api_key_sync_file() -> Optional[str]:
    """Load API key from config file synchronously."""
    config_file = Path('.pagespeed_config.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        except (json.JSONDecodeError, IOError):
            pass
    return None


async def load_api_key() -> Optional[str]:
    """Load Google PageSpeed API key from environment or config file."""
    # Check environment variable first (non-blocking)
    api_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    if api_key:
        return api_key

    # Offload file I/O to executor to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_api_key_sync_file)


# API Communication


async def test_page_speed(
    session: aiohttp.ClientSession,
    url: str,
    api_key: str,
    strategy: str = "mobile"
) -> Dict[str, Any]:
    """Test page speed using Google PageSpeed Insights API."""
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
        async with session.get(
            api_url, params=params, timeout=API_TIMEOUT
        ) as response:
            response.raise_for_status()
            # Read response body as text first
            text = await response.text()
            # Offload JSON parsing to executor to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, json.loads, text)
    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        return {"error": f"API request failed: {e}"}
    except asyncio.TimeoutError:
        return {"error": "API request timed out"}


# Data Extraction and Processing


def extract_core_web_vitals(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract Core Web Vitals from PageSpeed Insights data."""
    if "error" in data:
        return data

    try:
        lighthouse = data.get("lighthouseResult", EMPTY_DICT)
        audits = lighthouse.get("audits", EMPTY_DICT)

        config = lighthouse.get("configSettings", EMPTY_DICT)
        categories = lighthouse.get("categories", EMPTY_DICT)
        performance = categories.get("performance", EMPTY_DICT)

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "url": data.get("id", ""),
            "strategy": config.get("formFactor", ""),
            "performance_score": performance.get("score", 0) * 100,
        }

        for internal_key, audit_key, divisor in METRIC_MAP:
            value = audits.get(audit_key, EMPTY_DICT).get("numericValue", 0)
            metrics[internal_key] = value / divisor

        return metrics
    except Exception as e:
        return {"error": f"Failed to extract metrics: {e}"}


def analyze_performance(
    metrics: Dict[str, Any],
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Analyze performance metrics against defined thresholds."""
    if thresholds is None:
        thresholds = PERFORMANCE_THRESHOLDS

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
        if metric not in metrics:
            continue

        value = metrics[metric]
        if value <= threshold:
            continue

        analysis["overall_score"] = "FAIL"
        analysis["issues"].append(
            f"{metric}: {value:.2f} (threshold: {threshold})"
        )

        if metric in RECOMMENDATION_MAP:
            analysis["recommendations"].append(RECOMMENDATION_MAP[metric])

    return analysis


# Data Persistence


async def save_metrics_to_csv(metrics: List[Dict[str, Any]], filename: str):
    """Save performance metrics to CSV file asynchronously."""
    if not metrics:
        return

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, functools.partial(_save_metrics_to_csv_sync, metrics, filename)
    )


def _save_metrics_to_csv_sync(metrics: List[Dict[str, Any]], filename: str):
    """Internal synchronous function to save metrics to CSV."""
    fieldnames = metrics[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # Use loop to write rows individually, allowing frequent GIL release
        # to prevent blocking the event loop in the main thread.
        for row in metrics:
            writer.writerow(row)


# Reporting and Output


def generate_performance_report(analysis: Dict[str, Any]) -> str:
    """Generate a human-readable performance report."""
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


def print_strategy_results(strategy: str, analysis: Dict[str, Any]):
    """Print summary results for a specific strategy."""
    score = analysis.get('overall_score', 'N/A')
    issues_count = len(analysis.get('issues', []))

    print(f"📱 {strategy.capitalize()} Results:")
    print(f"  Performance Score: {score}")
    if issues_count > 0:
        print(f"  Issues Found: {issues_count}")
    else:
        print("  ✓ All metrics within thresholds")


# Main Execution


async def run_strategy_test(
    session: aiohttp.ClientSession,
    url: str,
    api_key: str,
    strategy: str
) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """Run a single strategy test asynchronously and process results."""
    print(f"\n📱 Starting {strategy} performance test...")

    # Test page speed
    result = await test_page_speed(session, url, api_key, strategy)
    if "error" in result:
        print(f"✗ Error testing {strategy}: {result['error']}")
        return None

    # Extract metrics
    metrics = extract_core_web_vitals(result)
    if "error" in metrics:
        print(f"✗ Error extracting metrics for {strategy}: {metrics['error']}")
        return None

    # Analyze performance
    analysis = analyze_performance(metrics)

    print_strategy_results(strategy, analysis)

    return metrics, analysis


async def async_main():
    """Async main function to run performance monitoring."""
    print("=" * 70)
    print("PERFORMANCE MONITORING FOR MAYTEN LANE WEBSITE")
    print("=" * 70)

    # Load API key
    api_key = await load_api_key()
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
        tasks = [
            run_strategy_test(session, WEBSITE_URL, api_key, strategy)
            for strategy in strategies
        ]
        results = await asyncio.gather(*tasks)

    # Filter out None results
    valid_results = [r for r in results if r is not None]

    # Save metrics to CSV
    all_metrics = [r[0] for r in valid_results]
    if all_metrics:
        await save_metrics_to_csv(all_metrics, OUTPUT_FILE)
        print(f"\n💾 Metrics saved to {OUTPUT_FILE}")

    # Generate and display final report
    if valid_results:
        print("\n" + "=" * 70)
        print("FINAL PERFORMANCE REPORT")
        print("=" * 70)

        # Optimization: Reuse analysis from test phase to avoid recomputation
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
