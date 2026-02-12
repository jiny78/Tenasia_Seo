from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.main import run


st.set_page_config(
    page_title="\ud150\uc544\uc2dc\uc544 SEO \ub77c\uc774\ube0c \ubd84\uc11d\uae30",
    page_icon="\U0001F4F0",
    layout="wide",
)


LABELS = {
    "title": "\uc81c\ubaa9 \ucd5c\uc801\ud654",
    "meta_description": "\uba54\ud0c0 \uc124\uba85",
    "headings": "\ud5e4\ub529 \uad6c\uc870",
    "content": "\ubcf8\ubb38 \ud488\uc9c8",
    "links": "\ub9c1\ud06c \uad6c\uc131",
    "images_alt": "\uc774\ubbf8\uc9c0 ALT",
    "readability": "\uac00\ub3c5\uc131",
}


def render_style() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap');

:root {
  --ink: #111827;
  --muted: #6b7280;
  --line: #e5e7eb;
  --card: rgba(255, 255, 255, 0.88);
}

.stApp {
  font-family: "IBM Plex Sans KR", sans-serif;
  background:
    radial-gradient(circle at 8% 18%, rgba(234, 88, 12, 0.14), transparent 22%),
    radial-gradient(circle at 88% 82%, rgba(14, 116, 144, 0.14), transparent 24%),
    linear-gradient(135deg, #fffaf4 0%, #fff 45%, #f7fbff 100%);
}

h1, h2, h3 {
  font-family: "Space Grotesk", "IBM Plex Sans KR", sans-serif !important;
  letter-spacing: -0.01em;
}

[data-testid="stMetric"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 10px 14px;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #fff 0%, #fff8f2 100%);
  border-right: 1px solid #f0e6de;
}

.hero-wrap {
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.88), rgba(255, 245, 238, 0.95));
  border: 1px solid #f0dfd2;
  border-radius: 18px;
  padding: 20px 22px;
  margin-bottom: 14px;
}

.hero-wrap .kicker {
  margin: 0;
  color: #9a3412;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.09em;
}

.hero-wrap .desc {
  color: var(--muted);
  margin: 8px 0 0 0;
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
    st.progress(percent, text=f"SEO \uc885\ud569 \uc810\uc218 {percent}%")


def render_article_overview(result: Dict[str, Any]) -> None:
    article = result["article"]
    st.subheader("\uae30\uc0ac \uac1c\uc694")
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


def render_detail_table(result: Dict[str, Any]) -> None:
    st.subheader("\uc138\ubd80 \ud56d\ubaa9 \uc810\uc218")
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
    st.subheader("\uac1c\uc120 \uad8c\uc7a5\uc0ac\ud56d")
    recs = result.get("recommendations", [])
    if not recs:
        st.success(
            "\uc989\uc2dc \uc870\uce58\ud560 \uc774\uc288\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. CTR/\uc21c\uc704\ub97c \ubaa8\ub2c8\ud130\ub9c1\ud558\uc138\uc694."
        )
        return
    for idx, rec in enumerate(recs, 1):
        lines = rec.split("\n", 1)
        st.markdown(f"{idx}. **{lines[0]}**")
        if len(lines) > 1:
            st.caption(lines[1])


def analyze(url: str) -> Dict[str, Any]:
    return run(url)


def main() -> None:
    render_style()
    st.markdown(
        """
<section class="hero-wrap">
  <p class="kicker">&#53584;&#50500;&#49884;&#50500; SEO LIVE</p>
  <h1>&#44592;&#49324; URL &#54616;&#45208;&#47196; SEO &#49345;&#53468;&#47484; &#48736;&#47476;&#44172; &#51652;&#45800;&#54633;&#45768;&#45796;</h1>
  <p class="desc">&#53356;&#47244;&#47553;, &#51216;&#49688; &#44228;&#49328;, &#44060;&#49440; &#44428;&#51109;&#49324;&#54637;&#51012; &#54620; &#48264;&#50640; &#54869;&#51064;&#54616;&#44256; &#48148;&#47196; &#49688;&#51221;&#51012; &#51652;&#54665;&#54624; &#49688; &#51080;&#49845;&#45768;&#45796;.</p>
</section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("\ubd84\uc11d \uc124\uc815")
        url = st.text_input("\uae30\uc0ac URL", value="https://example.com/article")
        auto_refresh = st.checkbox("60\ucd08 \uc790\ub3d9 \uc7ac\ubd84\uc11d", value=False)
        run_now = st.button("\uc9c0\uae08 \ubd84\uc11d", type="primary", use_container_width=True)
        if auto_refresh:
            st.caption("\uc790\ub3d9 \uc7ac\ubd84\uc11d\uc774 \ucf1c\uc838 \uc788\uc2b5\ub2c8\ub2e4. (60\ucd08)")
            st_autorefresh(interval=60_000, key="auto_refresh")

    if run_now or auto_refresh:
        with st.spinner("\uae30\uc0ac \ubd84\uc11d \uc911\uc785\ub2c8\ub2e4..."):
            result = analyze(url)

        if result["score"].get("error"):
            st.error(f"\ubd84\uc11d \uc2e4\ud328: {result['score']['error']}")
            return

        render_score_header(result)
        left, right = st.columns([1.2, 1])
        with left:
            render_detail_table(result)
        with right:
            render_recommendations(result)
        render_article_overview(result)

    else:
        st.info(
            "\uc0ac\uc774\ub4dc\ubc14\uc5d0 URL\uc744 \uc785\ub825\ud558\uace0 `\uc9c0\uae08 \ubd84\uc11d` \ubc84\ud2bc\uc744 \ub20c\ub7ec\uc8fc\uc138\uc694."
        )


if __name__ == "__main__":
    main()
