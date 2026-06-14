from pathlib import Path


def test_report_frontend_prefers_api_data_source():
    data_source = Path("web/report/src/data.ts").read_text(encoding="utf-8")

    assert "/api/report" in data_source


def test_report_frontend_navigation_is_two_tabs_only():
    render_source = Path("web/report/src/render.ts").read_text(encoding="utf-8")

    assert "技术资讯" in render_source
    assert "学术论文" in render_source
    assert "全部" not in render_source
    assert "行业标签" not in render_source
    assert "技术标签" not in render_source
    assert "文章类型" not in render_source
