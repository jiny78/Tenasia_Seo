import argparse
import json
from pathlib import Path

from src.crawler import fetch_article
from src.recommender import recommend_fixes
from src.scorer import score_article


def run(url: str) -> dict:
    rubric_path = Path(__file__).resolve().parents[1] / "configs" / "rubric.v1.json"
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))

    article = fetch_article(url)
    score_result = score_article(article, rubric)
    recommendations = recommend_fixes(score_result)

    return {
        "url": url,
        "article": article,
        "score": score_result,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze one article URL and print SEO report.")
    parser.add_argument("--url", default="https://example.com/article", help="Article URL")
    args = parser.parse_args()

    result = run(args.url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
