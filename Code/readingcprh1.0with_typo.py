import pandas as pd
import json
import os
import re
from typo_generation import (
    introduce_typo_to_sentence,
    drop_jongsung_sentence,
    repeat_char_typo_no_space,
    merge_words_typo,
    grammar_error,
    typo_dict
)

# <빈칸> 보존 함수
def preserve_placeholder(text, func, count):
    masked_text = re.sub(r"<빈칸>", "〈MASK〉", text)
    corrupted = func(masked_text, count)
    return corrupted.replace("〈MASK〉", "<빈칸>")

# CSV 불러오기
df = pd.read_csv("haerae_reading_comprehension.csv")

# 저장할 최상위 경로
base_dir = "hearea_rdcprhs1.0w/typo"
dataset_name = "HAERAE1.0_RC"

# 오타 함수 정의
typo_funcs = {
    "drop_jongsung": lambda txt, c: drop_jongsung_sentence(txt, count=c),
    "introduce_typo": lambda txt, c: introduce_typo_to_sentence(txt, count=c),
    "repeat_char": lambda txt, c: repeat_char_typo_no_space(txt, count=c, max_repeat=2),
    "merge_words": lambda txt, c: merge_words_typo(txt, count=c),
    "grammar_error": lambda txt, c: grammar_error(txt, typo_dict, count=c)
}

typo_variation = {
    "drop_jongsung": 1,
    "introduce_typo": 2,
    "repeat_char": 3,
    "merge_words": 4,
    "grammar_error": 5
}

for typo_type, func in typo_funcs.items():
    save_dir = os.path.join(base_dir, typo_type)
    os.makedirs(save_dir, exist_ok=True)

    typo_idx = typo_variation[typo_type]

    for count in range(1, 6):
        output_data = []

        for idx, row in df.iterrows():
            question_full = str(row["question"])
            if "참고:" not in question_full:
                continue

            prefix, body = question_full.split("참고:", 1)
            body = body.strip()

            # <빈칸>은 보존하면서 오타 적용
            typo_applied = preserve_placeholder(body, lambda txt, c=count: func(txt, c), count)
            new_question = f"{prefix}참고:{typo_applied}"

            output_data.append({
                "id": idx,
                "question": new_question,
                "a": row.get("a", ""),
                "b": row.get("b", ""),
                "c": row.get("c", ""),
                "d": row.get("d", ""),
                "answer": row.get("answer", ""),
                "split": row.get("split", "")
            })

        file_name = f"{dataset_name}_typo_{typo_idx}_level_{count}.json"
        file_path = os.path.join(save_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 저장 완료: {file_path}")
