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
    "ケロッグのコーンフレークは、トラのキャラクター「トニー・ザ・タイガー」でもおなじみの、"
    "世界中で愛されている砂糖がけのコーンフレークです。厳選したとうもろこしの粒を香ばしく焼き上げ、"
    "ほどよい砂糖をまぶしたサクサク食感のフレークに仕上げています。"
    "学校給食摂取基準に準拠したビタミンやミネラルなどの栄養バランスも満たしており、"
    "牛乳をかけるだけで手軽に美味しくエネルギーチャージができるシリアルです。"
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
