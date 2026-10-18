# jev-milkboy

This program plays Utsumi in Milkboy's cornflakes routine. For each hint Komaba gives about his mom's favorite breakfast, it asks TypeSafe AI's **Jev** whether the hint describes cornflakes, then answers "コーンフレークやないかい" (yes) or "ほなコーンフレークと違うかぁ" (no).

- Each hint goes to Jev as `state` (text), together with a yes/no question (`Noul`): "Does what this line describes fit cornflakes?"
- If the yes probability Jev returns is at or above `--threshold` (default 0.5), the reply is "コーンフレークやないかい". Otherwise it is "ほなコーンフレークと違うかぁ".
- The default model is `jev-latest`. You can change it with `--model`.

## Setup

[mise](https://mise.jdx.dev/) provides Python and [uv](https://docs.astral.sh/uv/), and uv installs the dependencies.

```sh
mise install                  # Install Python and uv as specified in mise.toml
uv sync --extra test          # Install into .venv exactly as locked in uv.lock
cp .env.example .env          # Put your TypeSafe AI API key in .env
```

Put your API key in `TYPESAFE_API_KEY` in `.env` and it is loaded at startup. If the environment variable is set, it takes precedence.

## Preparing the hints

`lines.txt` holds the lines from [this note article](https://note.com/mochicosan/n/nf1e3397cb7e5) where Komaba describes his mom's favorite breakfast, one hint per line.

- Blank lines and lines starting with `#` are ignored.
- See `lines.example.txt` for the format (its hints are made up, not taken from the routine).

## Usage

```sh
uv run jev-milkboy lines.txt                  # Read from a file
cat lines.txt | uv run jev-milkboy            # Read from stdin
uv run jev-milkboy lines.txt --threshold 0.7  # Require more confidence before calling it cornflakes
```

Sample output:

```
駒場: 甘くてサクサクしてて、牛乳をかけて食べるらしいねん
内海: コーンフレークやないかい (yes 0.97)

駒場: 炊きたてを茶碗によそって、お箸で食べるらしいねん
内海: ほなコーンフレークと違うかぁ (yes 0.02)

判定: 2/2  コーンフレークやないかい: 1  ほなコーンフレークと違うかぁ: 1  エラー: 0  モデル: ...  入力トークン: ...
```

(The probabilities above are only an illustration.) The output keeps the input order. A line that hits an API error shows `(判定失敗: ...)` and processing continues.

| Option | Default | Description |
|---|---|---|
| `file` | `-` (stdin) | Text file with one hint per line |
| `--model` | `jev-latest` | Model to use |
| `--threshold` | 0.5 | Minimum yes probability for "コーンフレークやないかい" |
| `--concurrency` | 8 | Number of concurrent requests |
| `--timeout` | 60 | Per-request timeout (seconds) |

## Tests

```sh
uv run pytest
```

The tests run offline, without an API key or network access.
