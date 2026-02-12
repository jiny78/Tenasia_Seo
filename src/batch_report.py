import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

from src.main import run


def load_urls(url_file: Path) -> List[str]:
    lines = url_file.read_text(encoding="utf-8").splitlines()
    urls: List[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        urls.append(cleaned)
    return urls


def build_report(urls: List[str]) -> dict:
    results = []
    for url in urls:
        results.append(run(url))
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(results),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SEO reports for multiple article URLs.")
    parser.add_argument(
        "--url-file",
        default="data/samples/urls.txt",
        help="Path to a text file containing one URL per line.",
    )
    parser.add_argument(
        "--output",
        default="data/reports/sample_report.json",
        help="Output path for report json.",
    )
    args = parser.parse_args()

    url_file = Path(args.url_file)
    output_path = Path(args.output)

    urls = load_urls(url_file)
    report = build_report(urls)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved report: {output_path} ({report['count']} urls)")


if __name__ == "__main__":
    main()
