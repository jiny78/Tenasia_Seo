from src.crawler import parse_article_html


def test_parse_article_html_extracts_basic_fields() -> None:
    html = """
    <html>
      <head>
        <title>Fallback Title</title>
        <meta name="description" content="meta desc" />
      </head>
      <body>
        <article>
          <h1>Heading One</h1>
          <h2>Section A</h2>
          <h2>Section B</h2>
          <p>First paragraph text.</p>
          <p>Second paragraph text.</p>
          <img src="a.jpg" alt="thumb" />
          <img src="b.jpg" />
          <a href="/inside">internal</a>
          <a href="https://external.example.com/page">external</a>
        </article>
      </body>
    </html>
    """

    result = parse_article_html("https://tenasia.example.com/post", html)

    assert result["title"] == "Fallback Title"
    assert result["meta_description"] == "meta desc"
    assert result["h1"] == "Heading One"
    assert result["h2_count"] == 2
    assert result["paragraph_count"] == 2
    assert result["image_count"] == 2
    assert result["images_missing_alt"] == 1
    assert result["internal_links"] == 1
    assert result["external_links"] == 1
    assert result["error"] == ""
