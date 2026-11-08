"""Ask Jev whether one of Komaba's hints describes cornflakes."""

from dataclasses import dataclass
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Image, Noul

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
CORNFLAKES_RECIPES = (
    "コーンフロスティ フレンチトースト：卵液でふやかしたフロスティをバターで焼き、フルーツと粉砂糖で仕上げるフレンチトースト風。",
    "コーンフロスティアイスクリーム：バニラアイスにフロスティをのせ、いちごとミントを添えるだけの5分デザート。",
    "コーンフロスティヨーグルトパフェ：ヨーグルトにキウイ・バナナ・ブルーベリーとフロスティを重ねたフルーツたっぷりのパフェ。",
    "トロピカルフロスティヨーグルト：マンゴー・キウイ・ヨーグルトにパイナップルジュースを合わせた南国風のフロスティボウル。",
    "ヨーグルトフルーツフロスティ：ヨーグルトにいちご・バナナ・ブルーベリーとフロスティを合わせた華やかな朝食ボウル。",
    "ヨーグルトフロスティココア：ココアを混ぜたヨーグルトにフロスティを合わせる、材料3つの簡単デザート。",
)
PACKAGE_DIR = Path(__file__).parent
CORNFLAKES_FRONT = Image(PACKAGE_DIR / "front.png")
CORNFLAKES_BACK = Image(PACKAGE_DIR / "back.png")
# Jev rejects requests that contain images unless this header is sent.
IMAGES_HEADERS = {"TypeSafe-Danger-Zone-Images": "true"}
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
        state={
            "line": line,
            "cornflakes_knowledge": CORNFLAKES_KNOWLEDGE,
            "cornflakes_recipes": list(CORNFLAKES_RECIPES),
            "cornflakes_package_front": CORNFLAKES_FRONT,
            "cornflakes_package_back": CORNFLAKES_BACK,
        },
        questions={QUESTION: Noul(instructions=INSTRUCTIONS, criteria=CRITERIA)},
        model=model,
        extra_headers=IMAGES_HEADERS,
    )
    return Judgement(
        probability=response.nouls[QUESTION].noul,
        model=response.model,
        input_tokens=response.usage.input_tokens,
    )
