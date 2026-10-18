"""Tests that run without an API key or network access."""

import asyncio

from jev_milkboy.judge import NO_REPLY, YES_REPLY, Judgement, reply
from jev_milkboy.main import Result, evaluate, format_result, read_lines, summary


def test_read_lines_skips_blank_and_comment_lines():
    text = "# comment\n\n  甘いらしいねん  \n\t\n#another\nしなしなになるらしいねん\n"
    assert read_lines(text) == ["甘いらしいねん", "しなしなになるらしいねん"]


def test_reply_threshold():
    assert reply(0.5) == YES_REPLY
    assert reply(0.49) == NO_REPLY
    assert reply(0.8, threshold=0.9) == NO_REPLY
    assert reply(0.1, threshold=0.1) == YES_REPLY


def test_evaluate_keeps_order_and_counts_errors():
    async def fake(line: str) -> Judgement:
        if line == "boom":
            raise RuntimeError("API down")
        # Finish later lines first to check the output order.
        await asyncio.sleep(0.01 * (3 - len(line)))
        return Judgement(probability=0.9 if line == "a" else 0.1, model="jev-test", input_tokens=5)

    results = asyncio.run(evaluate(["a", "bb", "boom"], fake, concurrency=2))
    assert [r.line for r in results] == ["a", "bb", "boom"]
    assert results[0].judgement.probability == 0.9
    assert results[2].judgement is None
    assert results[2].error == "RuntimeError: API down"


def test_format_and_summary():
    results = [
        Result("甘いらしいねん", Judgement(0.97, "jev-test", 10)),
        Result("お箸で食べるらしいねん", Judgement(0.03, "jev-test", 12)),
        Result("壊れた", None, "RuntimeError: x"),
    ]
    assert format_result(results[0], 0.5) == f"駒場: 甘いらしいねん\n内海: {YES_REPLY} (yes 0.97)"
    assert format_result(results[1], 0.5) == f"駒場: お箸で食べるらしいねん\n内海: {NO_REPLY} (yes 0.03)"
    assert format_result(results[2], 0.5) == "駒場: 壊れた\n内海: (判定失敗: RuntimeError: x)"
    line = summary(results, 0.5)
    assert "判定: 2/3" in line
    assert f"{YES_REPLY}: 1" in line
    assert f"{NO_REPLY}: 1" in line
    assert "エラー: 1" in line
    assert "入力トークン: 22" in line
