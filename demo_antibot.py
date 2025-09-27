#!/usr/bin/env python3
"""
Demo script showing antibot evasion capabilities.

This script demonstrates the antibot functionality by running the scraper
with antibot measures enabled and showing the evasion techniques in action.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from scraper import scrape_mall_directory


def demo_antibot_evasion() -> None:
    """Demonstrate antibot evasion capabilities."""

    print("🚀 Google Maps Mall Scraper - Antibot Evasion Demo")
    print("=" * 60)

    # Enable real scraping for demo (normally would be False for safety)
    os.environ["GOOGLEMAPSMALL_REAL_SCRAPING"] = "true"

    print("\n🔧 Enabling antibot evasion mode...")
    print("📱 Using realistic user agents and browser fingerprints")
    print("🐭 Implementing human-like mouse movements and delays")
    print("⏱️  Adding randomized timing patterns")
    print("🔄 Integrating proxy rotation capabilities")

    # Test URL for St James Quarter mall
    mall_url = "https://www.google.com/maps/place/St+James+Quarter"
    strategy = {"strategy": "view_all", "antibot_level": "high", "max_categories": 3}

    print(f"\n🎯 Target: {mall_url}")
    print(f"📋 Strategy: {strategy['strategy']}")
    print(f"🛡️  Antibot Level: {strategy['antibot_level']}")

    start_time = time.time()
    print("\n⏳ Starting antibot-enabled scraping session...")

    try:
        # Run the scraper with antibot measures
        result = scrape_mall_directory(mall_url, strategy)

        duration = time.time() - start_time

        print("\n✅ Scraping completed successfully!")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Brands extracted: {len(result.get('brands', []))}")
        print(f"📂 Categories found: {len(result.get('categories', []))}")

        # Show antibot metadata
        metadata = result.get("metadata", {})
        if metadata.get("antibot_enabled"):
            print("\n🛡️  Antibot Measures Applied:")
            measures = metadata.get("antibot_measures_applied", [])
            for measure in measures:
                if measure:
                    print(f"   ✓ {measure.replace('_', ' ').title()}")

        print("\n📈 Success Metrics:")
        print(f"   Interactions: {metadata.get('interactions_performed', 0)}")
        print(f"   Success Rate: {metadata.get('success_rate', 0):.1%}")

        # Show sample brands
        brands = result.get("brands", [])[:3]  # Show first 3
        if brands:
            print("\n🏪 Sample Brands Extracted:")
            for brand in brands:
                print(
                    f"   • {brand['name']} ({brand['category']}) - "
                    f"{brand['confidence_score']:.1%}"
                )

        print("\n🎉 Demo completed! Antibot evasion system is operational.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print(
            "This is expected in demo mode without full Playwright MCP " "integration."
        )

    finally:
        # Reset environment
        os.environ.pop("GOOGLEMAPSMALL_REAL_SCRAPING", None)


def show_antibot_features() -> None:
    """Show the key antibot features implemented."""

    print("\n🛡️  Antibot Evasion Features Implemented:")
    print("-" * 40)

    features = [
        "Realistic User Agent Rotation",
        "Human-like Mouse Movement Simulation",
        "Randomized Delay Patterns (500ms-2000ms)",
        "Session Persistence & Cookie Management",
        "Proxy Rotation Integration",
        "Browser Fingerprint Variation",
        "Rate Limiting Avoidance",
        "Geolocation Permission Handling",
        "HAR Capture During Interactions",
        "Error Recovery Without Detection Triggers",
        "Antibot Detection & Recovery Logic",
    ]

    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature}")
    print()


if __name__ == "__main__":
    show_antibot_features()
    demo_antibot_evasion()
