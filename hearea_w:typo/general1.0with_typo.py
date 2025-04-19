import pandas as pd
import json
import os
from typo_generation import (
    introduce_typo_to_sentence,
    drop_jongsung_sentence,
    repeat_char_typo_no_space,
    merge_words_typo,
    grammar_error,
    typo_dict
)

# CSV 불러오기
df = pd.read_csv("haerae_general_knowledge.csv")

# 저장할 최상위 경로
base_dir = "hearea_gnrknw1.0w/typo"

# 오타 함수 정의
typo_funcs = {
    "introduce_typo": lambda txt, c: introduce_typo_to_sentence(txt, count=c),
    "drop_jongsung": lambda txt, c: drop_jongsung_sentence(txt, count=c),
    "repeat_char": lambda txt, c: repeat_char_typo_no_space(txt, count=c, max_repeat=2),
    "merge_words": lambda txt, c: merge_words_typo(txt, count=c),
    "grammar_error": lambda txt, c: grammar_error(txt, typo_dict, count=c)
}

# 각 오타 타입별 폴더 만들고 저장
for typo_type, func in typo_funcs.items():
    save_dir = os.path.join(base_dir, typo_type)
    os.makedirs(save_dir, exist_ok=True)

    for count in range(1, 6):  # 오타 1~5회
        output_data = []

        for idx, row in df.iterrows():
            question_full = str(row["question"])
            if "참고:" not in question_full:
                continue

            prefix, body = question_full.split("참고:", 1)
            body = body.strip()

            typo_applied = func(body, count)
            new_question = f"{prefix}참고:{typo_applied}"

            output_data.append({
                "id": idx,
                "question": new_question,
                "a": row.get("a", ""),
                "b": row.get("b", ""),
                "c": row.get("c", ""),
                "d": row.get("d", ""),
                "e": row.get("e", ""),
                "answer": row.get("answer", ""),
                "split": row.get("split", "")
            })

        # 저장 경로
        file_path = os.path.join(save_dir, f"typo_{count}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 저장 완료: {file_path}")
