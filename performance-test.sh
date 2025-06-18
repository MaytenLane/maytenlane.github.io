#!/bin/bash

# Mayten Lane Website Performance Test Script
# This script tests various aspects of website performance and SEO

echo "🚀 Mayten Lane Website Performance Test"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test URLs
URLS=(
    "https://www.maytenlane.com"
    "https://maytenlane.com"
    "http://www.maytenlane.com"
    "http://maytenlane.com"
)

echo -e "${BLUE}1. Testing URL Redirects and Status Codes${NC}"
echo "----------------------------------------"

for url in "${URLS[@]}"; do
    echo -n "Testing $url: "
    
    # Get HTTP status and redirect chain
    response=$(curl -s -o /dev/null -w "%{url_effective} %{http_code} %{redirect_url} %{time_total}s" -L "$url")
    
    # Parse response
    final_url=$(echo $response | cut -d' ' -f1)
    status_code=$(echo $response | cut -d' ' -f2)
    redirect_url=$(echo $response | cut -d' ' -f3)
    load_time=$(echo $response | cut -d' ' -f4)
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✓ $status_code${NC} (${load_time}s)"
    elif [ "$status_code" = "301" ] || [ "$status_code" = "302" ]; then
        echo -e "${YELLOW}→ $status_code${NC} → $redirect_url (${load_time}s)"
    else
        echo -e "${RED}✗ $status_code${NC} (${load_time}s)"
    fi
done

echo ""
echo -e "${BLUE}2. Testing Page Load Performance${NC}"
echo "--------------------------------"

# Test main page performance
echo -n "Testing main page load time: "
main_load=$(curl -s -o /dev/null -w "%{time_total}" https://www.maytenlane.com)
echo -e "${GREEN}${main_load}s${NC}"

# Test with different user agents
echo -n "Testing mobile user agent: "
mobile_load=$(curl -s -o /dev/null -w "%{time_total}" -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15" https://www.maytenlane.com)
echo -e "${GREEN}${mobile_load}s${NC}"

echo ""
echo -e "${BLUE}3. Testing HTTP Headers${NC}"
echo "---------------------------"

# Check important headers
echo -n "Checking HTTPS enforcement: "
https_check=$(curl -s -I http://maytenlane.com | grep -i "location" | grep -i "https")
if [ ! -z "$https_check" ]; then
    echo -e "${GREEN}✓ HTTPS redirect working${NC}"
else
    echo -e "${RED}✗ HTTPS redirect not working${NC}"
fi

echo -n "Checking cache headers: "
cache_check=$(curl -s -I https://www.maytenlane.com | grep -i "cache-control")
if [ ! -z "$cache_check" ]; then
    echo -e "${GREEN}✓ Cache headers present${NC}"
else
    echo -e "${YELLOW}⚠ No cache headers found${NC}"
fi

echo -n "Checking security headers: "
security_check=$(curl -s -I https://www.maytenlane.com | grep -i "x-frame-options\|x-content-type-options\|x-xss-protection")
if [ ! -z "$security_check" ]; then
    echo -e "${GREEN}✓ Security headers present${NC}"
else
    echo -e "${YELLOW}⚠ Some security headers missing${NC}"
fi

echo ""
echo -e "${BLUE}4. Testing File Sizes${NC}"
echo "----------------------"

# Check HTML file size
html_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.maytenlane.com)
echo -n "HTML file size: "
if [ "$html_size" -lt 50000 ]; then
    echo -e "${GREEN}${html_size} bytes ✓${NC}"
else
    echo -e "${YELLOW}${html_size} bytes ⚠${NC}"
fi

# Check CSS file size
css_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.maytenlane.com/style.css)
echo -n "CSS file size: "
if [ "$css_size" -lt 10000 ]; then
    echo -e "${GREEN}${css_size} bytes ✓${NC}"
else
    echo -e "${YELLOW}${css_size} bytes ⚠${NC}"
fi

echo ""
echo -e "${BLUE}5. Testing SEO Elements${NC}"
echo "---------------------------"

# Check for important SEO elements
echo -n "Checking canonical URL: "
canonical_check=$(curl -s https://www.maytenlane.com | grep -i "canonical")
if [ ! -z "$canonical_check" ]; then
    echo -e "${GREEN}✓ Canonical URL present${NC}"
else
    echo -e "${RED}✗ Canonical URL missing${NC}"
fi

echo -n "Checking meta description: "
meta_desc_check=$(curl -s https://www.maytenlane.com | grep -i "meta.*description")
if [ ! -z "$meta_desc_check" ]; then
    echo -e "${GREEN}✓ Meta description present${NC}"
else
    echo -e "${RED}✗ Meta description missing${NC}"
fi

echo -n "Checking Open Graph tags: "
og_check=$(curl -s https://www.maytenlane.com | grep -i "og:")
if [ ! -z "$og_check" ]; then
    echo -e "${GREEN}✓ Open Graph tags present${NC}"
else
    echo -e "${RED}✗ Open Graph tags missing${NC}"
fi

echo -n "Checking structured data: "
schema_check=$(curl -s https://www.maytenlane.com | grep -i "application/ld\\+json")
if [ ! -z "$schema_check" ]; then
    echo -e "${GREEN}✓ Structured data present${NC}"
else
    echo -e "${RED}✗ Structured data missing${NC}"
fi

echo ""
echo -e "${BLUE}6. Testing Accessibility${NC}"
echo "---------------------------"

# Check for alt text on images
echo -n "Checking image alt text: "
alt_check=$(curl -s https://www.maytenlane.com | grep -i "img.*alt")
if [ ! -z "$alt_check" ]; then
    echo -e "${GREEN}✓ Alt text present on images${NC}"
else
    echo -e "${RED}✗ Alt text missing on images${NC}"
fi

# Check for semantic HTML
echo -n "Checking semantic HTML: "
semantic_check=$(curl -s https://www.maytenlane.com | grep -i "main\|header\|footer\|nav")
if [ ! -z "$semantic_check" ]; then
    echo -e "${GREEN}✓ Semantic HTML elements present${NC}"
else
    echo -e "${YELLOW}⚠ Limited semantic HTML elements${NC}"
fi

echo ""
echo -e "${BLUE}7. Testing External Resources${NC}"
echo "--------------------------------"

# Check external resource loading
echo -n "Testing FontAwesome loading: "
fa_check=$(curl -s -I https://use.fontawesome.com/releases/v6.4.2/css/all.css | head -1)
if [[ $fa_check == *"200"* ]]; then
    echo -e "${GREEN}✓ FontAwesome accessible${NC}"
else
    echo -e "${RED}✗ FontAwesome not accessible${NC}"
fi

echo -n "Testing Google Analytics: "
ga_check=$(curl -s -I https://www.googletagmanager.com/gtag/js | head -1)
if [[ $ga_check == *"200"* ]]; then
    echo -e "${GREEN}✓ Google Analytics accessible${NC}"
else
    echo -e "${RED}✗ Google Analytics not accessible${NC}"
fi

echo ""
echo -e "${BLUE}8. Testing Sitemap and Robots${NC}"
echo "--------------------------------"

# Check sitemap
echo -n "Testing sitemap accessibility: "
sitemap_check=$(curl -s -I https://www.maytenlane.com/sitemap.xml | head -1)
if [[ $sitemap_check == *"200"* ]]; then
    echo -e "${GREEN}✓ Sitemap accessible${NC}"
else
    echo -e "${RED}✗ Sitemap not accessible${NC}"
fi

# Check robots.txt
echo -n "Testing robots.txt accessibility: "
robots_check=$(curl -s -I https://www.maytenlane.com/robots.txt | head -1)
if [[ $robots_check == *"200"* ]]; then
    echo -e "${GREEN}✓ Robots.txt accessible${NC}"
else
    echo -e "${RED}✗ Robots.txt not accessible${NC}"
fi

echo ""
echo -e "${BLUE}9. Performance Recommendations${NC}"
echo "-----------------------------------"

# Performance score calculation
score=0
max_score=20

# Add points for good performance
if (( $(echo "$main_load < 1.0" | bc -l) )); then
    score=$((score + 2))
fi
if [ "$html_size" -lt 50000 ]; then
    score=$((score + 2))
fi
if [ "$css_size" -lt 10000 ]; then
    score=$((score + 2))
fi
if [ ! -z "$canonical_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$meta_desc_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$og_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$schema_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$alt_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$semantic_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$https_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$cache_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$sitemap_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$robots_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$fa_check" ]; then
    score=$((score + 1))
fi
if [ ! -z "$ga_check" ]; then
    score=$((score + 1))
fi

# Calculate percentage
percentage=$((score * 100 / max_score))

echo -n "Overall Performance Score: "
if [ $percentage -ge 90 ]; then
    echo -e "${GREEN}$score/$max_score ($percentage%) - Excellent!${NC}"
elif [ $percentage -ge 80 ]; then
    echo -e "${GREEN}$score/$max_score ($percentage%) - Very Good${NC}"
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}$score/$max_score ($percentage%) - Good${NC}"
elif [ $percentage -ge 60 ]; then
    echo -e "${YELLOW}$score/$max_score ($percentage%) - Fair${NC}"
else
    echo -e "${RED}$score/$max_score ($percentage%) - Needs Improvement${NC}"
fi

echo ""
echo -e "${BLUE}10. Quick Recommendations${NC}"
echo "----------------------------"

if [ "$html_size" -gt 50000 ]; then
    echo -e "${YELLOW}⚠ Consider minifying HTML${NC}"
fi

if [ "$css_size" -gt 10000 ]; then
    echo -e "${YELLOW}⚠ Consider minifying CSS${NC}"
fi

if [ -z "$security_check" ]; then
    echo -e "${YELLOW}⚠ Consider adding security headers${NC}"
fi

if (( $(echo "$main_load > 2.0" | bc -l) )); then
    echo -e "${YELLOW}⚠ Page load time could be improved${NC}"
fi

echo ""
echo "✅ Performance test completed!"
echo "Run this script regularly to monitor website performance." 