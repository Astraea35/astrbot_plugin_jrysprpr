import asyncio
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

from astrbot.api.message_components import Image, Plain
from astrbot_plugin_jrysprpr.main import JrysPlugin


@pytest.mark.asyncio
async def test_telegram_jrys_outputs_photo_and_caption():
    plugin = JrysPlugin.__new__(JrysPlugin)
    plugin.resources = SimpleNamespace(
        _load_jrys_data=AsyncMock(return_value={
            "90": [{"fortuneSummary": "大吉", "signText": "诸事皆宜", "unsignText": "诸事不忌", "luckyStar": "★★★★★"}],
            "60": [{"fortuneSummary": "平稳"}],
            "30": [{"fortuneSummary": "谨慎"}],
        }),
        get_background_image=AsyncMock(return_value=(
            str(Path(__file__).resolve().parents[1] / "README.assets" / "1.jpg"),
            False,
        )),
        data_dir=str(Path(__file__).resolve().parents[1]),
    )
    plugin.painter = SimpleNamespace(
        select_fortune=lambda user_key, data: data["90"][0]
    )

    sent_chains = []
    sent_plains = []

    event = SimpleNamespace(
        get_platform_name=lambda: "telegram",
        get_sender_id=lambda: "123456",
        get_sender_name=lambda: "测试用户",
        chain_result=lambda chain: sent_chains.append(chain) or chain,
        plain_result=lambda text: sent_plains.append(text) or text,
    )

    results = [res async for res in plugin.jrys(event)]
    assert len(results) == 1
    assert len(sent_chains) == 1
    chain = sent_chains[0]
    assert isinstance(chain[0], Image)
    assert isinstance(chain[1], Plain)

    text = chain[1].text
    assert "🔮 **今日运势 · 每日一签**" in text
    assert "签主：`测试用户`" in text
    assert "✨ **【 大吉 】**  🌟 幸运指数：`★★★★★`" in text
    assert "> 🟢 **【宜】** 诸事皆宜" in text
    assert "> 🔴 **【忌】** 诸事不忌" in text
    assert "💡 *运势仅供娱乐参考，心向阳光万事皆安*" in text
