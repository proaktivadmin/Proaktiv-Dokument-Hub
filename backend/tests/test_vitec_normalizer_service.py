from app.services.vitec_normalizer_service import VitecNormalizerService


def test_normalizer_removes_proaktiv_branding_rules():
    html = """
    <div id="vitecTemplate">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
        h1 { font-family: Georgia, serif; color: #272630; }
        .highlight-box { border: 1px solid #bcab8a; padding: 20px; }
      </style>
      <h1>Title</h1>
      <div class="highlight-box">Content</div>
    </div>
    """
    normalizer = VitecNormalizerService()
    normalized, report = normalizer.normalize(html)

    assert 'vitec-template="resource:Vitec Stilark"' in normalized
    assert "@import" not in normalized
    assert "highlight-box" not in normalized
    assert "font-family" not in normalized
    assert int(report["removed_css_rules"]) >= 1


def test_normalizer_keeps_vitec_functional_css():
    html = """
    <div id="vitecTemplate">
      <style>
        #vitecTemplate table { border-collapse: collapse; width: 100%; }
        #vitecTemplate table td[data-label]:before { content: attr(data-label); font-size: 9pt; }
        .svg-toggle.checkbox { background-image: url("data:image/svg+xml;utf8,abc"); }
      </style>
      <table><tr><td data-label="Test">Cell</td></tr></table>
    </div>
    """
    normalizer = VitecNormalizerService()
    normalized, report = normalizer.normalize(html)

    assert "border-collapse" in normalized
    assert "data-label" in normalized
    assert "svg-toggle" in normalized
    assert int(report["kept_css_rules"]) >= 1


def test_normalizer_inline_style_policy_keeps_form_lines():
    html = """
    <div id="vitecTemplate">
      <table>
        <tr>
          <td style="border-bottom: solid 1px #000000; font-size: 12pt; color: #272630;">&nbsp;</td>
        </tr>
      </table>
    </div>
    """
    normalizer = VitecNormalizerService()
    normalized, _ = normalizer.normalize(html)

    assert "border-bottom: solid 1px #000000" in normalized
    assert "font-size" not in normalized
    assert "color" not in normalized
