#!/usr/bin/env python3
"""Debug script to find image URLs on employee pages."""

import re

import httpx
from bs4 import BeautifulSoup

url = "https://proaktiv.no/eiendomsmegler/drammen-lier/proaktiv-drammen-lier-holmestrand/alexander-abelseth"
resp = httpx.get(url, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
html = resp.text

# Look for .jpg URLs in the HTML
jpg_pattern = re.compile(r"https?://[^\s\"'<>]+\.jpg[^\s\"'<>]*", re.IGNORECASE)
matches = jpg_pattern.findall(html)
print("=== JPG URLs found ===")
for m in set(matches):
    if "proaktiv" in m.lower():
        print(m[:150])

# Look for webp URLs
webp_pattern = re.compile(r"https?://[^\s\"'<>]+\.webp[^\s\"'<>]*", re.IGNORECASE)
webp_matches = webp_pattern.findall(html)
print("\n=== WEBP URLs found ===")
for m in set(webp_matches):
    if "proaktiv" in m.lower():
        print(m[:150])

# Look for style attributes with background
soup = BeautifulSoup(html, "lxml")
print("\n=== Elements with style containing url( ===")
for el in soup.find_all(style=re.compile(r"url\(")):
    style = el.get("style", "")
    print(f"Tag: {el.name}, style: {style[:200]}")

# Look for data-bg or similar attributes
print("\n=== Elements with data-bg or similar ===")
for el in soup.find_all(attrs={"data-bg": True}):
    print(f"data-bg: {el.get('data-bg')}")
for el in soup.find_all(attrs={"data-background": True}):
    print(f"data-background: {el.get('data-background')}")
for el in soup.find_all(attrs={"data-src": True}):
    src = el.get("data-src", "")
    if "jpg" in src.lower() or "webp" in src.lower():
        print(f"data-src: {src[:150]}")
