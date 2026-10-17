"""Maintainers only: rebuild grading/answer_key.json from solutions/quiz-answers.yaml.

    docker compose run --rm --entrypoint python grader grading/tools/build_answer_key.py
"""
import hashlib
import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
source = yaml.safe_load((REPO / "solutions" / "quiz-answers.yaml").read_text(encoding="utf-8"))
key = {
    module: {q: hashlib.sha256(f"hol|{module}|{q}|{letter.upper()}".encode()).hexdigest()
             for q, letter in questions.items()}
    for module, questions in source.items()
}
(REPO / "grading" / "answer_key.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
print(f"answer_key.json written: {sum(len(v) for v in key.values())} questions in {len(key)} modules")
