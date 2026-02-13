import json
from pathlib import Path

from src.recommender import recommend_fixes
from src.scorer import score_article


def _load_rubric() -> dict:
    rubric_path = Path(__file__).resolve().parents[1] / "configs" / "rubric.v1.json"
    return json.loads(rubric_path.read_text(encoding="utf-8"))


def test_score_article_and_recommend() -> None:
    article = {
        "url": "https://example.com/post",
        "title": "Short",
        "meta_description": "",
        "h1": "",
        "h2_count": 0,
        "content": "One short sentence.",
        "word_count": 3,
        "image_count": 2,
        "images_missing_alt": 2,
        "internal_links": 0,
        "external_links": 0,
        "error": "",
    }
    rubric = _load_rubric()

    score_result = score_article(article, rubric)
    fixes = recommend_fixes(score_result)

    assert score_result["total_score"] < 60
    assert len(score_result["details"]) == 7
    assert len(fixes) > 0


def test_entertainment_short_form_profile_relaxes_h2_and_word_rules() -> None:
    article = {
        "url": "https://example.com/news/photo/123",
        "title": "아이돌 A 포토 공개",
        "meta_description": "아이돌 A의 현장 포토가 공개됐다. 스타일링 포인트를 확인할 수 있다.",
        "h1": "아이돌 A 포토 공개",
        "h2_count": 0,
        "content": "아이돌 A가 행사장 포토월에 섰다. 팬 반응이 이어졌다.",
        "word_count": 16,
        "paragraph_count": 2,
        "image_count": 1,
        "images_missing_alt": 0,
        "internal_links": 1,
        "external_links": 0,
        "error": "",
    }
    rubric = _load_rubric()

    score_result = score_article(article, rubric)
    details = {item["id"]: item for item in score_result["details"]}

    assert score_result["profile"]["domain"] == "entertainment_news"
    assert score_result["profile"]["format"] == "short_form"
    assert "h2_insufficient" not in details["headings"]["issues"]
    assert "internal_links_insufficient" not in details["links"]["issues"]


def test_short_form_complete_facts_not_forced_long_body() -> None:
    article = {
        "url": "https://example.com/photo/999",
        "title": "Actor A photo release",
        "meta_description": "Actor A photo was released today with teaser cuts.",
        "h1": "Actor A photo release",
        "h2_count": 0,
        "content": "Actor A released teaser photos today. The agency announced the schedule.",
        "word_count": 22,
        "paragraph_count": 2,
        "image_count": 1,
        "images_missing_alt": 0,
        "internal_links": 1,
        "external_links": 0,
        "error": "",
    }
    rubric = _load_rubric()

    score_result = score_article(article, rubric)
    details = {item["id"]: item for item in score_result["details"]}

    assert score_result["profile"]["domain"] == "entertainment_news"
    assert score_result["profile"]["format"] == "short_form"
    assert "content_too_short" not in details["content"]["issues"]
