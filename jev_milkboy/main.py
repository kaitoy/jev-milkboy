"""Command-line entry point: give Komaba's hints to Jev and print Utsumi's comebacks."""

import argparse
import asyncio
import sys
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from jev_milkboy.judge import DEFAULT_THRESHOLD, YES_REPLY, Judgement, judge, reply

DEFAULT_MODEL = "jev-latest"

Judge = Callable[[str], Awaitable[Judgement]]


@dataclass
class Result:
    line: str
    judgement: Judgement | None
    error: str | None = None


def read_lines(text: str) -> list[str]:
    """One hint per line; blank lines and lines starting with # are skipped."""
    return [s for s in (raw.strip() for raw in text.splitlines()) if s and not s.startswith("#")]


async def evaluate(lines: Sequence[str], judge_line: Judge, *, concurrency: int) -> list[Result]:
    """Judge every line in parallel and return the results in input order."""
    semaphore = asyncio.Semaphore(concurrency)

    async def run(line: str) -> Result:
        async with semaphore:
            try:
                return Result(line, await judge_line(line))
            except Exception as error:  # noqa: BLE001 - Report API failures per line instead of aborting the routine.
                return Result(line, None, f"{type(error).__name__}: {error}")

    return list(await asyncio.gather(*(run(line) for line in lines)))


def format_result(result: Result, threshold: float) -> str:
    if result.judgement is None:
        comeback = f"(判定失敗: {result.error})"
    else:
        p = result.judgement.probability
        comeback = f"{reply(p, threshold)} (yes {p:.2f})"
    return f"駒場: {result.line}\n内海: {comeback}"


def summary(results: Sequence[Result], threshold: float) -> str:
    judged = [r.judgement for r in results if r.judgement is not None]
    yes = sum(reply(j.probability, threshold) == YES_REPLY for j in judged)
    parts = [
        f"判定: {len(judged)}/{len(results)}",
        f"コーンフレークやないかい: {yes}",
        f"ほなコーンフレークと違うかぁ: {len(judged) - yes}",
        f"エラー: {len(results) - len(judged)}",
    ]
    models = sorted({j.model for j in judged})
    if models:
        parts.append(f"モデル: {', '.join(models)}")
    parts.append(f"入力トークン: {sum(j.input_tokens for j in judged)}")
    return "  ".join(parts)


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask Jev whether each of Komaba's hints describes cornflakes.")
    parser.add_argument("file", nargs="?", default="-", help="text file with one hint per line (default: - for stdin)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"model name (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"yes probability at or above which it is cornflakes (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument("--concurrency", type=int, default=8, help="parallel requests (default: 8)")
    parser.add_argument("--timeout", type=float, default=60.0, help="per-request timeout in seconds (default: 60)")
    return parser.parse_args(argv)


async def run(args: argparse.Namespace) -> int:
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    lines = read_lines(text)
    if not lines:
        print("No hints to judge.", file=sys.stderr)
        return 1

    from typesafe_sdk import AsyncTypeSafeClient

    async with AsyncTypeSafeClient(timeout=args.timeout) as client:
        results = await evaluate(lines, lambda line: judge(client, line, args.model), concurrency=args.concurrency)
    print("\n\n".join(format_result(r, args.threshold) for r in results))
    print()
    print(summary(results, args.threshold))
    return 0 if any(r.judgement for r in results) else 1


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv()  # Read TYPESAFE_API_KEY etc. from .env; real environment variables take precedence.
    return asyncio.run(run(parse_args(argv)))


if __name__ == "__main__":
    sys.exit(main())
