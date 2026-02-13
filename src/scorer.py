import re
from typing import Any, Dict, List, Tuple


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


ENTERTAINMENT_KEYWORDS = (
    "comeback",
    "teaser",
    "photo",
    "interview",
    "idol",
    "actor",
    "singer",
    "drama",
    "\ucef4\ubc31",
    "\ud2f0\uc800",
    "\ud3ec\ud1a0",
    "\ud654\ubcf4",
    "\uc544\uc774\ub3cc",
    "\ubc30\uc6b0",
    "\uac00\uc218",
    "\uc778\ud130\ubdf0",
)

SHORT_FORM_KEYWORDS = (
    "photo",
    "video",
    "breaking",
    "clip",
    "\ud3ec\ud1a0",
    "\uc0ac\uc9c4",
    "\uc601\uc0c1",
    "\uc18d\ubcf4",
    "\ud604\uc7a5",
)


def _detect_profile(article: Dict[str, Any]) -> Dict[str, Any]:
    title = (article.get("title") or "").lower()
    url = (article.get("url") or "").lower()
    content = (article.get("content") or "").lower()
    word_count = int(article.get("word_count") or 0)
    paragraph_count = int(article.get("paragraph_count") or 0)

    entertainment_hits = sum(1 for kw in ENTERTAINMENT_KEYWORDS if kw in title or kw in content)
    short_form_hits = sum(1 for kw in SHORT_FORM_KEYWORDS if kw in title or kw in url)

    is_entertainment = entertainment_hits >= 1
    is_short_form = short_form_hits >= 1 or (word_count <= 180 and paragraph_count <= 4)
    is_deep_dive = word_count >= 350 and paragraph_count >= 6

    if is_entertainment and is_short_form:
        fmt = "short_form"
    elif is_entertainment and is_deep_dive:
        fmt = "deep_dive"
    else:
        fmt = "standard"

    return {
        "domain": "entertainment_news" if is_entertainment else "general_news",
        "format": fmt,
    }


def _apply_profile_rules(
    criterion_id: str,
    rules: Dict[str, Any],
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    adjusted = dict(rules)
    domain = profile.get("domain")
    fmt = profile.get("format")

    if domain != "entertainment_news":
        return adjusted

    if criterion_id == "headings":
        if fmt == "short_form":
            adjusted["target_h2_count"] = 0
            adjusted["h1_required"] = False
        elif fmt == "standard":
            adjusted["target_h2_count"] = min(int(adjusted.get("target_h2_count", 2)), 1)
            adjusted["soft_h1_if_title_present"] = True
        elif fmt == "deep_dive":
            adjusted["soft_h1_if_title_present"] = True
    elif criterion_id == "content":
        if fmt == "short_form":
            adjusted["min_word_count"] = 110
            adjusted["ideal_word_count"] = 220
        elif fmt == "standard":
            adjusted["min_word_count"] = 170
            adjusted["ideal_word_count"] = 320
        elif fmt == "deep_dive":
            adjusted["min_word_count"] = 260
            adjusted["ideal_word_count"] = 520
    elif criterion_id == "links":
        adjusted["min_internal_links"] = 1
        adjusted["require_external_links"] = False
    elif criterion_id == "readability":
        if fmt == "short_form":
            adjusted["ideal_min_avg_sentence_words"] = 8
            adjusted["ideal_max_avg_sentence_words"] = 22
        else:
            adjusted["ideal_min_avg_sentence_words"] = 10
            adjusted["ideal_max_avg_sentence_words"] = 24

    return adjusted


def _content_signals(article: Dict[str, Any]) -> Dict[str, bool]:
    title = (article.get("title") or "").lower()
    content = (article.get("content") or "").lower()
    text = f"{title} {content}"

    subject_markers = (
        "\uc544\uc774\ub3cc",
        "\ubc30\uc6b0",
        "\uac00\uc218",
        "\uba64\ubc84",
        "\uadf8\ub8f9",
        "actor",
        "singer",
        "group",
    )
    event_markers = (
        "\uacf5\uac1c",
        "\ubc1c\ud45c",
        "\ucd9c\uc5f0",
        "\ucef4\ubc31",
        "\uac1c\ucd5c",
        "\uc5f4\uc560",
        "\uacb0\ud63c",
        "release",
        "announce",
        "comeback",
        "interview",
    )

    has_subject = any(marker in text for marker in subject_markers)
    has_event = any(marker in text for marker in event_markers)

    has_time_context = bool(
        re.search(
            r"(오늘|어제|내일|지난|오는|오전|오후|방송|공개일|현지시간|[0-9]{1,2}월\s*[0-9]{1,2}일|[0-9]{4}-[0-9]{2}-[0-9]{2})",
            text,
        )
    )

    return {
        "has_subject": has_subject,
        "has_event": has_event,
        "has_time_context": has_time_context,
    }


def _score_title(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    title = (article.get("title") or "").strip()
    length = len(title)
    issues: List[str] = []

    if not title:
        return {
            "id": "title",
            "weight": weight,
            "score": 0,
            "issues": ["title_missing"],
            "metrics": {"title_length": 0},
        }

    score = float(weight)
    if length < rules.get("min_length", 35):
        score -= weight * 0.6
        issues.append("title_too_short")
    elif length > rules.get("max_length", 70):
        score -= weight * 0.5
        issues.append("title_too_long")
    elif not (rules.get("ideal_min_length", 50) <= length <= rules.get("ideal_max_length", 60)):
        score -= weight * 0.2
        issues.append("title_not_ideal_length")

    return {
        "id": "title",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"title_length": length},
    }


def _score_meta(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    meta = (article.get("meta_description") or "").strip()
    length = len(meta)
    issues: List[str] = []
    if not meta:
        return {
            "id": "meta_description",
            "weight": weight,
            "score": 0,
            "issues": ["meta_description_missing"],
            "metrics": {"meta_description_length": 0},
        }

    score = float(weight)
    if length < rules.get("min_length", 70):
        score -= weight * 0.6
        issues.append("meta_description_too_short")
    elif length > rules.get("max_length", 180):
        score -= weight * 0.5
        issues.append("meta_description_too_long")
    elif not (
        rules.get("ideal_min_length", 120) <= length <= rules.get("ideal_max_length", 160)
    ):
        score -= weight * 0.2
        issues.append("meta_description_not_ideal_length")

    return {
        "id": "meta_description",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"meta_description_length": length},
    }


def _score_headings(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    h1 = (article.get("h1") or "").strip()
    h2_count = int(article.get("h2_count") or 0)
    issues: List[str] = []
    score = float(weight)

    if rules.get("h1_required", True) and not h1:
        if rules.get("soft_h1_if_title_present", False) and (article.get("title") or "").strip():
            score -= weight * 0.25
            issues.append("h1_missing_soft")
        else:
            score -= weight * 0.7
            issues.append("h1_missing")

    target_h2 = int(rules.get("target_h2_count", 2))
    if h2_count < target_h2:
        score -= weight * 0.3
        issues.append("h2_insufficient")

    return {
        "id": "headings",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"h1_present": bool(h1), "h2_count": h2_count},
    }


def _score_content(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    word_count = int(article.get("word_count") or 0)
    issues: List[str] = []
    score = float(weight)
    profile = article.get("_profile", {})
    is_entertainment = profile.get("domain") == "entertainment_news"
    content_signals = _content_signals(article)

    min_words = int(rules.get("min_word_count", 300))
    ideal_words = int(rules.get("ideal_word_count", 700))

    if is_entertainment:
        penalty_ratio = 0.0
        if not content_signals["has_subject"]:
            penalty_ratio += 0.28
            issues.append("content_missing_subject")
        if not content_signals["has_event"]:
            penalty_ratio += 0.35
            issues.append("content_missing_event")
        if not content_signals["has_time_context"]:
            penalty_ratio += 0.22
            issues.append("content_missing_time_context")

        core_complete = (
            content_signals["has_subject"]
            and content_signals["has_event"]
            and content_signals["has_time_context"]
        )
        if word_count < min_words and (word_count < 60 or not core_complete):
            penalty_ratio += 0.12
            issues.append("content_too_short")
        elif word_count < ideal_words:
            penalty_ratio += 0.06
            issues.append("content_below_ideal_length")

        score -= weight * min(penalty_ratio, 0.9)
    else:
        if word_count < min_words:
            score -= weight * 0.7
            issues.append("content_too_short")
        elif word_count < ideal_words:
            score -= weight * 0.2
            issues.append("content_below_ideal_length")

    return {
        "id": "content",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"word_count": word_count, **content_signals},
    }


def _score_links(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    internal_links = int(article.get("internal_links") or 0)
    external_links = int(article.get("external_links") or 0)
    issues: List[str] = []
    score = float(weight)

    if internal_links < int(rules.get("min_internal_links", 2)):
        score -= weight * 0.5
        issues.append("internal_links_insufficient")
    # 뉴스 서비스 특성상 외부 출처 링크는 필수가 아니므로 감점하지 않는다.
    if rules.get("require_external_links", False) and external_links < int(
        rules.get("min_external_links", 1)
    ):
        score -= weight * 0.5
        issues.append("external_links_missing")

    return {
        "id": "links",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"internal_links": internal_links, "external_links": external_links},
    }


def _score_images_alt(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    image_count = int(article.get("image_count") or 0)
    missing_alt = int(article.get("images_missing_alt") or 0)
    allow_missing_alt = int(rules.get("allow_missing_alt", 0))
    issues: List[str] = []
    score = float(weight)

    if image_count > 0 and missing_alt > allow_missing_alt:
        missing_ratio = missing_alt / image_count
        score -= weight * _clamp(missing_ratio, 0, 1)
        issues.append("images_missing_alt")

    return {
        "id": "images_alt",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {"image_count": image_count, "images_missing_alt": missing_alt},
    }


def _sentence_stats(content: str) -> Tuple[int, float]:
    text = (content or "").strip()
    if not text:
        return 0, 0.0
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0, 0.0
    words = [token for token in re.split(r"\s+", text) if token]
    return len(sentences), len(words) / len(sentences)


def _score_readability(article: Dict[str, Any], weight: int, rules: Dict[str, Any]) -> Dict[str, Any]:
    content = article.get("content") or ""
    sentence_count, avg_sentence_words = _sentence_stats(content)
    issues: List[str] = []
    score = float(weight)

    min_avg = float(rules.get("min_avg_sentence_words", 8))
    max_avg = float(rules.get("max_avg_sentence_words", 30))
    ideal_min = float(rules.get("ideal_min_avg_sentence_words", 12))
    ideal_max = float(rules.get("ideal_max_avg_sentence_words", 25))

    if sentence_count == 0:
        score = 0
        issues.append("readability_not_measurable")
    elif avg_sentence_words < min_avg:
        score -= weight * 0.6
        issues.append("sentences_too_short")
    elif avg_sentence_words > max_avg:
        score -= weight * 0.6
        issues.append("sentences_too_long")
    elif not (ideal_min <= avg_sentence_words <= ideal_max):
        score -= weight * 0.2
        issues.append("sentence_length_not_ideal")

    return {
        "id": "readability",
        "weight": weight,
        "score": round(_clamp(score, 0, weight), 2),
        "issues": issues,
        "metrics": {
            "sentence_count": sentence_count,
            "avg_sentence_words": round(avg_sentence_words, 2),
        },
    }


SCORERS = {
    "title": _score_title,
    "meta_description": _score_meta,
    "headings": _score_headings,
    "content": _score_content,
    "links": _score_links,
    "images_alt": _score_images_alt,
    "readability": _score_readability,
}


def score_article(article: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
    criteria = rubric.get("criteria", [])
    details: List[Dict[str, Any]] = []
    total_score = 0.0
    total_weight = 0.0
    profile = _detect_profile(article)
    article = dict(article)
    article["_profile"] = profile

    if article.get("error"):
        return {
            "total_score": 0,
            "max_score": rubric.get("total", 100),
            "grade": "F",
            "details": [],
            "error": article["error"],
        }

    for criterion in criteria:
        criterion_id = criterion.get("id")
        weight = int(criterion.get("weight", 0))
        rules = _apply_profile_rules(criterion_id, criterion.get("rules", {}), profile)
        scorer = SCORERS.get(criterion_id)
        if not scorer or weight <= 0:
            continue

        item = scorer(article, weight, rules)
        details.append(item)
        total_score += float(item["score"])
        total_weight += weight

    max_score = float(rubric.get("total", total_weight or 100))
    normalized = (total_score / total_weight * max_score) if total_weight else 0.0
    normalized = round(_clamp(normalized, 0, max_score), 2)

    if normalized >= 90:
        grade = "A"
    elif normalized >= 80:
        grade = "B"
    elif normalized >= 70:
        grade = "C"
    elif normalized >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "total_score": normalized,
        "max_score": max_score,
        "grade": grade,
        "details": details,
        "profile": profile,
        "error": "",
    }
