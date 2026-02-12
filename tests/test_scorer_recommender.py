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
