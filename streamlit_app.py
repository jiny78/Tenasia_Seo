import json
from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.main import run


st.set_page_config(
    page_title="Tenasia SEO Live Analyzer",
    page_icon=":newspaper:",
    layout="wide",
)


LABELS = {
    "title": "Title",
    "meta_description": "Meta Description",
    "headings": "Headings",
    "content": "Content",
    "links": "Links",
    "images_alt": "Image Alt",
    "readability": "Readability",
}


def _score_color(score: float, weight: float) -> str:
    ratio = score / weight if weight else 0
    if ratio >= 0.8:
        return "green"
    if ratio >= 0.6:
        return "orange"
    return "red"


def render_score_header(result: Dict[str, Any]) -> None:
    score = result["score"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Score", f"{score['total_score']:.1f}/{score['max_score']:.0f}")
    col2.metric("Grade", score["grade"])
    col3.metric("Analyzed At (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))


def render_article_overview(result: Dict[str, Any]) -> None:
    article = result["article"]
    st.subheader("Article Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Words", article.get("word_count", 0))
    col2.metric("Paragraphs", article.get("paragraph_count", 0))
    col3.metric("Internal Links", article.get("internal_links", 0))
    col4.metric("External Links", article.get("external_links", 0))

    with st.expander("Extracted Metadata", expanded=False):
        st.write(f"Title: {article.get('title', '')}")
        st.write(f"H1: {article.get('h1', '')}")
        st.write(f"H2 Count: {article.get('h2_count', 0)}")
        st.write(f"Meta Description: {article.get('meta_description', '')}")


def render_detail_table(result: Dict[str, Any]) -> None:
    st.subheader("Criteria Details")
    details = result["score"].get("details", [])
    if not details:
        st.info("No detail rows.")
        return

    rows = []
    for item in details:
        score = float(item.get("score", 0))
        weight = float(item.get("weight", 0))
        rows.append(
            {
                "criteria": LABELS.get(item.get("id", ""), item.get("id", "")),
                "score": f"{score:.1f}/{weight:.0f}",
                "status": _score_color(score, weight),
                "issues": ", ".join(item.get("issues", [])) or "-",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_recommendations(result: Dict[str, Any]) -> None:
    st.subheader("Recommended Fixes")
    recs = result.get("recommendations", [])
    if not recs:
        st.success("No immediate fixes. Keep monitoring CTR and ranking.")
        return
    for idx, rec in enumerate(recs, 1):
        st.markdown(f"{idx}. {rec}")


def analyze(url: str) -> Dict[str, Any]:
    return run(url)


def main() -> None:
    st.title("Tenasia SEO Live Analyzer")
    st.caption("Enter an article URL to run live crawl, scoring, and recommendations.")

    with st.sidebar:
        st.header("Controls")
        default_url = "https://example.com/article"
        url = st.text_input("Article URL", value=default_url)
        auto_refresh = st.checkbox("Auto refresh every 60s", value=False)
        run_now = st.button("Run Analysis", type="primary", use_container_width=True)
        if auto_refresh:
            st.caption("Auto refresh is enabled (60s).")
            st_autorefresh(interval=60_000, key="auto_refresh")

    if run_now or auto_refresh:
        with st.spinner("Analyzing article..."):
            result = analyze(url)

        if result["score"].get("error"):
            st.error(f"Analysis failed: {result['score']['error']}")
            return

        render_score_header(result)
        left, right = st.columns([1.2, 1])
        with left:
            render_detail_table(result)
        with right:
            render_recommendations(result)

        render_article_overview(result)

        st.subheader("Raw JSON")
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")
        st.download_button(
            "Download Result JSON",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="seo_result.json",
            mime="application/json",
            use_container_width=True,
        )
    else:
        st.info("Set URL in sidebar and click Run Analysis.")


if __name__ == "__main__":
    main()
