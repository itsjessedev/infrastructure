#!/usr/bin/env python3
"""
Image Downloader using Playwright
Downloads images from article pages or direct URLs, bypassing hotlink protection.
"""

import sys
import os
import argparse
from pathlib import Path
from urllib.parse import urlparse
import base64
from playwright.sync_api import sync_playwright

def download_image_from_article(page, url, output_path, selector=None):
    """
    Navigate to article page and download the main image.

    Args:
        page: Playwright page object
        url: Article URL
        output_path: Where to save the image
        selector: CSS selector for specific image (optional)
    """
    print(f"Loading page: {url}")
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=15000)
        # Wait a bit for dynamic content
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Warning during page load: {e}")

    # First, try og:image meta tag (most reliable)
    try:
        meta = page.locator('meta[property="og:image"]').first
        if meta:
            img_url = meta.get_attribute('content')
            if img_url:
                print(f"Found og:image: {img_url}")
                return download_direct_image(page, img_url, output_path)
    except:
        pass

    # If specific selector provided, use it
    if selector:
        try:
            img = page.locator(selector).first
            if img:
                src = img.get_attribute('src', timeout=5000)
                if src:
                    return download_direct_image(page, src, output_path)
        except:
            pass

    # Try to find the main article image
    # Common selectors for news sites
    selectors = [
        'article img',
        'img[class*="featured"]',
        'img[class*="hero"]',
        'img[class*="lead"]',
        'img[data-src]',  # Lazy loaded images
        'figure img',
        'picture img',
        'div[class*="image"] img',
        'img',  # Fallback to any img
    ]

    img = None
    src = None
    for sel in selectors:
        try:
            locator = page.locator(sel)
            count = locator.count()
            if count > 0:
                # Try first few images
                for i in range(min(count, 3)):
                    try:
                        candidate = locator.nth(i)
                        if candidate.is_visible(timeout=1000):
                            # Get src or data-src
                            src = candidate.get_attribute('src', timeout=1000)
                            if not src:
                                src = candidate.get_attribute('data-src', timeout=1000)
                            if src and len(src) > 20:  # Ignore tiny icons
                                img = candidate
                                break
                    except:
                        continue
            if img and src:
                break
        except:
            continue

    if not img or not src:
        print(f"Warning: Could not find image on page")
        return False

    print(f"Found image element with src")

    if not src:
        print("Warning: Image has no src attribute")
        return False

    # Handle relative URLs
    if src.startswith('//'):
        src = 'https:' + src
    elif src.startswith('/'):
        parsed = urlparse(url)
        src = f"{parsed.scheme}://{parsed.netloc}{src}"

    print(f"Found image: {src}")

    # Download the image
    return download_direct_image(page, src, output_path)

def download_direct_image(page, url, output_path):
    """
    Download image from direct URL using the browser context.

    Args:
        page: Playwright page object
        url: Direct image URL
        output_path: Where to save
    """
    try:
        # Use page.goto to load the image with browser context
        response = page.goto(url)
        if response and response.status == 200:
            # Get the image data
            image_data = response.body()

            # Save to file
            with open(output_path, 'wb') as f:
                f.write(image_data)

            size_kb = len(image_data) / 1024
            print(f"✓ Downloaded: {output_path.name} ({size_kb:.1f} KB)")
            return True
        else:
            print(f"✗ Failed to download (status: {response.status if response else 'unknown'})")
            return False
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return False

def screenshot_element(page, url, output_path, selector=None):
    """
    Take a screenshot of a specific element or full page.
    Useful for tweets, social media posts, etc.

    Args:
        page: Playwright page object
        url: Page URL
        output_path: Where to save screenshot
        selector: CSS selector for specific element (optional)
    """
    print(f"Loading page for screenshot: {url}")
    page.goto(url, wait_until='networkidle')

    if selector:
        element = page.locator(selector).first
        if element:
            element.screenshot(path=str(output_path))
            print(f"✓ Screenshot saved: {output_path.name}")
            return True
        else:
            print(f"✗ Could not find element: {selector}")
            return False
    else:
        page.screenshot(path=str(output_path), full_page=True)
        print(f"✓ Full page screenshot saved: {output_path.name}")
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Download images from web pages using Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download main image from article
  %(prog)s -u "https://nytimes.com/article" -o image.jpg

  # Download with specific CSS selector
  %(prog)s -u "https://site.com/page" -o image.jpg -s "article img.main"

  # Screenshot a tweet
  %(prog)s -u "https://twitter.com/user/status/123" -o tweet.png --screenshot -s "article"

  # Batch download from URLs file
  %(prog)s --batch urls.txt -d ./output/
        '''
    )

    parser.add_argument('-u', '--url', help='Page URL to download from')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-s', '--selector', help='CSS selector for specific image/element')
    parser.add_argument('-d', '--output-dir', help='Output directory (default: current)', default='.')
    parser.add_argument('--screenshot', action='store_true', help='Take screenshot instead of downloading image')
    parser.add_argument('--batch', help='File containing URLs (one per line)')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode (default)')
    parser.add_argument('--headed', action='store_true', help='Run with visible browser (for debugging)')

    args = parser.parse_args()

    if not args.url and not args.batch:
        parser.error("Either --url or --batch is required")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    headless = args.headless and not args.headed

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        if args.batch:
            # Batch mode: read URLs from file
            batch_file = Path(args.batch)
            if not batch_file.exists():
                print(f"Error: Batch file not found: {batch_file}")
                return 1

            with open(batch_file) as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            print(f"Processing {len(urls)} URLs from {batch_file}")

            for i, url in enumerate(urls, 1):
                # Generate output filename from URL
                parsed = urlparse(url)
                filename = f"image_{i}.jpg"
                output_path = output_dir / filename

                print(f"\n[{i}/{len(urls)}]")
                if args.screenshot:
                    screenshot_element(page, url, output_path, args.selector)
                else:
                    download_image_from_article(page, url, output_path, args.selector)

        else:
            # Single URL mode
            if not args.output:
                parser.error("--output is required when using --url")

            output_path = output_dir / args.output

            if args.screenshot:
                screenshot_element(page, args.url, output_path, args.selector)
            else:
                download_image_from_article(page, args.url, output_path, args.selector)

        browser.close()

    print("\n✓ Done!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
