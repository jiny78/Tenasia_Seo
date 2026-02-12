import re
from urllib.parse import urlparse
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup, Tag

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _extract_meta(soup: BeautifulSoup, key: str) -> str:
    tag = soup.find("meta", attrs={"name": key}) or soup.find(
        "meta", attrs={"property": key}
    )
    if not tag:
        return ""
    return _clean_text(tag.get("content", ""))


def _extract_title(soup: BeautifulSoup) -> str:
    og_title = _extract_meta(soup, "og:title")
    if og_title:
        return og_title
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)
    return ""


def _select_article_root(soup: BeautifulSoup) -> Tag:
    selectors = [
        "article",
        "[itemprop='articleBody']",
        "#articleBody",
        ".article_body",
        ".article-body",
        ".article-view",
        ".article_view",
        ".news-body",
        ".news_cnt_detail_wrap",
        ".view_cont",
    ]
    for selector in selectors:
        node = soup.select_one(selector)
        if isinstance(node, Tag):
            return node
    return soup.body if isinstance(soup.body, Tag) else soup


def _extract_paragraphs(root: Tag) -> List[str]:
    paragraphs = [_clean_text(p.get_text(" ", strip=True)) for p in root.find_all("p")]
    paragraphs = [p for p in paragraphs if p]
    if paragraphs:
        return paragraphs

    fallback = _clean_text(root.get_text(" ", strip=True))
    return [fallback] if fallback else []


def _count_links(root: Tag, base_url: str) -> Dict[str, int]:
    base_domain = urlparse(base_url).netloc.lower()
    internal = 0
    external = 0
    for link in root.find_all("a", href=True):
        href = link["href"].strip()
        if not href:
            continue
        parsed = urlparse(href)
        if not parsed.netloc:
            internal += 1
            continue
        if parsed.netloc.lower() == base_domain:
            internal += 1
        else:
            external += 1
    return {"internal_links": internal, "external_links": external}


def parse_article_html(url: str, html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    title = _extract_title(soup)
    meta_description = _extract_meta(soup, "description") or _extract_meta(
        soup, "og:description"
    )
    h1_node = soup.find("h1")
    h1 = _clean_text(h1_node.get_text(" ", strip=True)) if h1_node else ""

    root = _select_article_root(soup)
    paragraphs = _extract_paragraphs(root)
    content = "\n".join(paragraphs)
    words = len([token for token in re.split(r"\s+", content) if token])

    images = root.find_all("img")
    images_missing_alt = sum(1 for img in images if not _clean_text(img.get("alt", "")))
    link_counts = _count_links(root, url)

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "h1": h1,
        "h2_count": len(root.find_all("h2")),
        "content": content,
        "paragraph_count": len(paragraphs),
        "word_count": words,
        "image_count": len(images),
        "images_missing_alt": images_missing_alt,
        "internal_links": link_counts["internal_links"],
        "external_links": link_counts["external_links"],
        "error": "",
    }


def fetch_article(url: str) -> Dict[str, Any]:
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {
            "url": url,
            "title": "",
            "meta_description": "",
            "h1": "",
            "h2_count": 0,
            "content": "",
            "paragraph_count": 0,
            "word_count": 0,
            "image_count": 0,
            "images_missing_alt": 0,
            "internal_links": 0,
            "external_links": 0,
            "error": str(exc),
        }

    article = parse_article_html(response.url, response.text)
    article["status_code"] = response.status_code
    return article
