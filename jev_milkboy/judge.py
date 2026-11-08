"""Ask Jev whether one of Komaba's hints describes cornflakes."""

from dataclasses import dataclass

from typesafe_sdk import AsyncTypeSafeClient, Noul

QUESTION = "cornflakes"
INSTRUCTIONS = (
    "このセリフが説明している特徴は、コーンフレークに当てはまりますか？"
)
CRITERIA = {
    "true": "セリフの特徴がコーンフレークに当てはまる。",
    "false": "セリフの特徴はコーンフレークには当てはまらない（他の食べ物の特徴など）。",
}
CORNFLAKES_KNOWLEDGE = (
    "ケロッグのコーンフレークは、厳選された自然の恵みのコーンを独自の製法で香ばしく焼き上げた、"
    "甘くないロングセラーのシリアルです。1食（40g）あたりで6種類のビタミンと鉄分をバランスよく摂ることができ、"
    "栄養機能食品（鉄）としても認められています。そのまま食べるのはもちろん、"
    "牛乳をかけて手軽に栄養のある朝食を楽しめるのが特徴です。"
)
YES_REPLY ="コーンフレークやないかい"
NO_REPLY = "ほなコーンフレークと違うかぁ"
DEFAULT_THRESHOLD = 0.5


@dataclass(frozen=True)
class Judgement:
    probability: float  # Jev's probability that the hint describes cornflakes, from 0 to 1.
    model: str
    input_tokens: int


def reply(probability: float, threshold: float = DEFAULT_THRESHOLD) -> str:
    """Utsumi's comeback: cornflakes at or above the threshold, not cornflakes below it."""
    return YES_REPLY if probability >= threshold else NO_REPLY


async def judge(client: AsyncTypeSafeClient, line: str, model: str) -> Judgement:
    response = await client.system_one(
        state={"line": line, "cornflakes_knowledge": CORNFLAKES_KNOWLEDGE},
        questions={QUESTION: Noul(instructions=INSTRUCTIONS, criteria=CRITERIA)},
        model=model,
    )
    return Judgement(
        probability=response.nouls[QUESTION].noul,
        model=response.model,
        input_tokens=response.usage.input_tokens,
    )
