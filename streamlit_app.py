from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.main import run


st.set_page_config(
    page_title="\ud150\uc544\uc2dc\uc544 SEO \uc2a4\ud29c\ub514\uc624",
    page_icon="\U0001F4F0",
    layout="wide",
)


LABELS = {
    "title": "\uc81c\ubaa9 \ucd5c\uc801\ud654",
    "meta_description": "\uba54\ud0c0 \uc124\uba85",
    "headings": "\ud5e4\ub529 \uad6c\uc870",
    "content": "\ubcf8\ubb38 \ud488\uc9c8",
    "links": "\ub0b4\ubd80 \ub9c1\ud06c \uad6c\uc131",
    "images_alt": "\uc774\ubbf8\uc9c0 ALT",
    "readability": "\uac00\ub3c5\uc131",
}


def render_style() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=Sora:wght@500;700;800&display=swap');

:root {
  --ink: #e5e7eb;
  --muted: #94a3b8;
  --line: #1f2937;
  --card: rgba(15, 23, 42, 0.74);
  --accent: #f43f5e;
  --accent-2: #fb7185;
  --deep: #f8fafc;
}

.stApp {
  font-family: "IBM Plex Sans KR", sans-serif;
  background:
    radial-gradient(circle at 12% 14%, rgba(244, 63, 94, 0.2), transparent 26%),
    radial-gradient(circle at 88% 86%, rgba(56, 189, 248, 0.16), transparent 24%),
    linear-gradient(140deg, #000000 0%, #05070d 45%, #0b1120 100%);
}

h1, h2, h3 {
  font-family: "Sora", "IBM Plex Sans KR", sans-serif !important;
  color: var(--deep);
  letter-spacing: -0.01em;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #030712 0%, #0b1220 100%);
  border-right: 1px solid #1f2937;
}

[data-testid="stMetric"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 12px 14px;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.34);
}

[data-testid="stMetricLabel"] {
  color: var(--muted);
}

[data-testid="stMetricValue"] {
  color: #f8fafc;
}

.hero {
  background:
    linear-gradient(120deg, rgba(2, 6, 23, 0.98) 0%, rgba(15, 23, 42, 0.98) 60%, rgba(244, 63, 94, 0.9) 100%);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 22px;
  padding: 26px 26px 24px;
  color: #f8fafc;
  margin-bottom: 14px;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.28);
}

.hero .kicker {
  margin: 0 0 10px;
  font: 700 12px/1 "Sora", sans-serif;
  letter-spacing: 0.14em;
  color: #fde68a;
}

.hero h1 {
  margin: 0;
  color: #ffffff;
  font: 800 clamp(26px, 4vw, 44px)/1.1 "Sora", sans-serif;
}

.hero .desc {
  margin: 12px 0 0;
  color: #dbeafe;
  max-width: 920px;
}

.panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 10px 12px 2px;
}

.panel-title {
  margin: 2px 0 8px;
  font: 700 15px/1.2 "Sora", sans-serif;
  color: var(--deep);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _score_state(score: float, weight: float) -> str:
    ratio = score / weight if weight else 0.0
    if ratio >= 0.8:
        return "\uc6b0\uc218"
    if ratio >= 0.6:
        return "\ubcf4\ud1b5"
    return "\uac1c\uc120 \ud544\uc694"


def analyze(url: str) -> Dict[str, Any]:
    return run(url)


def render_header() -> None:
    st.markdown(
        """
<section class="hero">
  <p class="kicker">&#53584;&#50500;&#49884;&#50500; SEO STUDIO</p>
  <h1>&#44592;&#49324; &#51089;&#49457; &#54980; 10&#52488; &#50504;&#50640; SEO&#51216;&#44160;</h1>
  <p class="desc">&#51216;&#49688; &#48372;&#44592; -> &#48148;&#47196; &#49688;&#51221; -> &#51116;&#48516;&#49437; &#55120;&#47492;&#51012; &#50684;&#45716; &#53584;&#50500;&#49884;&#50500; &#51204;&#50857; SEO &#54868;&#47732;&#51077;&#45768;&#45796;.</p>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_score_header(result: Dict[str, Any]) -> None:
    score = result["score"]
    total_score = float(score.get("total_score", 0))
    max_score = float(score.get("max_score", 100))
    percent = int((total_score / max_score) * 100) if max_score else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("\ucd1d\uc810", f"{total_score:.1f}/{max_score:.0f}")
    col2.metric("\ub4f1\uae09", score.get("grade", "-"))
    col3.metric(
        "\ubd84\uc11d \uc2dc\uac01 (UTC)",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )
    st.progress(percent, text=f"\uc885\ud569 \uc644\uc131\ub3c4 {percent}%")


def render_detail_table(result: Dict[str, Any]) -> None:
    details = result["score"].get("details", [])
    if not details:
        st.info("\uc138\ubd80 \uc810\uc218 \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.")
        return

    rows = []
    for item in details:
        score = float(item.get("score", 0))
        weight = float(item.get("weight", 0))
        rows.append(
            {
                "\ud56d\ubaa9": LABELS.get(item.get("id", ""), item.get("id", "")),
                "\uc810\uc218": f"{score:.1f}/{weight:.0f}",
                "\uc0c1\ud0dc": _score_state(score, weight),
                "\uc774\uc288": ", ".join(item.get("issues", [])) or "-",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_recommendations(result: Dict[str, Any]) -> None:
    recs = result.get("recommendations", [])
    if not recs:
        st.success(
            "\uc989\uc2dc \uc870\uce58\ud560 \uc774\uc288\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc81c\ubaa9/\uba54\ud0c0 \uc124\uba85 A-B \ud14c\uc2a4\ud2b8\ub9cc \uc9c4\ud589\ud558\uc138\uc694."
        )
        return
    for idx, rec in enumerate(recs, 1):
        lines = rec.split("\n", 1)
        st.markdown(f"{idx}. **{lines[0]}**")
        if len(lines) > 1:
            st.caption(lines[1])


def render_article_overview(result: Dict[str, Any]) -> None:
    article = result["article"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("\ub2e8\uc5b4 \uc218", article.get("word_count", 0))
    col2.metric("\ubb38\ub2e8 \uc218", article.get("paragraph_count", 0))
    col3.metric("\ub0b4\ubd80 \ub9c1\ud06c", article.get("internal_links", 0))
    col4.metric("\uc678\ubd80 \ub9c1\ud06c", article.get("external_links", 0))

    with st.expander("\ucd94\ucd9c \uba54\ud0c0\ub370\uc774\ud130", expanded=False):
        st.write(f"\uc81c\ubaa9: {article.get('title', '')}")
        st.write(f"H1: {article.get('h1', '')}")
        st.write(f"H2 \uac1c\uc218: {article.get('h2_count', 0)}")
        st.write(f"\uba54\ud0c0 \uc124\uba85: {article.get('meta_description', '')}")


def main() -> None:
    render_style()
    render_header()

    with st.sidebar:
        st.header("\ubd84\uc11d \uc81c\uc5b4")
        url = st.text_input("\uae30\uc0ac URL", value="https://example.com/article")
        auto_refresh = st.checkbox("60\ucd08 \uc790\ub3d9 \uc7ac\ubd84\uc11d", value=False)
        run_now = st.button("\uc9c0\uae08 \ubd84\uc11d", type="primary", use_container_width=True)
        st.caption("\ud301: \uae30\uc0ac \ucd08\uace0 \uc218\uc815 \ud6c4 \uc989\uc2dc \ub2e4\uc2dc \ubd84\uc11d\ud558\uc138\uc694.")
        if auto_refresh:
            st_autorefresh(interval=60_000, key="auto_refresh")

    if not (run_now or auto_refresh):
        st.info(
            "\uc0ac\uc774\ub4dc\ubc14\uc5d0 URL\uc744 \uc785\ub825\ud558\uace0 `\uc9c0\uae08 \ubd84\uc11d` \ubc84\ud2bc\uc744 \ub20c\ub7ec\uc8fc\uc138\uc694."
        )
        return

    with st.spinner("\ud150\uc544\uc2dc\uc544 \uae30\uc0ac SEO\ub97c \ubd84\uc11d \uc911\uc785\ub2c8\ub2e4..."):
        result = analyze(url)

    if result["score"].get("error"):
        st.error(f"\ubd84\uc11d \uc2e4\ud328: {result['score']['error']}")
        return

    st.markdown('<div class="panel"><p class="panel-title">\uc885\ud569 \uc810\uc218</p></div>', unsafe_allow_html=True)
    render_score_header(result)

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown('<div class="panel"><p class="panel-title">\ud56d\ubaa9\ubcc4 \uc810\uc218 \uc0c1\uc138</p></div>', unsafe_allow_html=True)
        render_detail_table(result)
    with right:
        st.markdown('<div class="panel"><p class="panel-title">\uc218\uc815 \uc6b0\uc120\uc21c\uc704 \ubc0f \uc608\uc2dc</p></div>', unsafe_allow_html=True)
        render_recommendations(result)

    st.markdown('<div class="panel"><p class="panel-title">\uae30\uc0ac \uac1c\uc694</p></div>', unsafe_allow_html=True)
    render_article_overview(result)


if __name__ == "__main__":
    main()
