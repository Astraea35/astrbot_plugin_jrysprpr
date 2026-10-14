import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "fortune_painter_test", Path(__file__).resolve().parents[1] / "painter.py",
)
painter_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(painter_module)


def test_daily_fortune_is_stable_without_qq_avatar_or_image_rendering():
    painter = painter_module.FortunePainter.__new__(painter_module.FortunePainter)
    painter.fixed_daily_fortune = True
    painter.holiday_rates_enabled = False
    painter.normal_rates = {"good": 40, "normal": 40, "bad": 20}
    data = {
        "90": [{"fortuneSummary": "大吉", "signText": "读书"}],
        "60": [{"fortuneSummary": "平稳"}],
        "30": [{"fortuneSummary": "谨慎"}],
        "_user_last_images": {"private-id": {"path": "private-file"}},
    }
    assert painter.select_fortune("tg:123", data) == painter.select_fortune("tg:123", data)
    assert painter.select_fortune("qq:456", data) in (data["90"] + data["60"] + data["30"])
