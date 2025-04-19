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
df = pd.read_csv("haerae1.1_reading_comprehension.csv")

# 저장할 최상위 폴더
base_dir = "hearea_rdcprhs1.1w/typo"

# 데이터셋 이름 설정
dataset_name = "HAERAE1.1_RC"

# 오타 함수들
typo_funcs = {
    "drop_jongsung": lambda txt, c: drop_jongsung_sentence(txt, count=c),
    "introduce_typo": lambda txt, c: introduce_typo_to_sentence(txt, count=c),
    "repeat_char": lambda txt, c: repeat_char_typo_no_space(txt, count=c, max_repeat=2),
    "merge_words": lambda txt, c: merge_words_typo(txt, count=c),
    "grammar_error": lambda txt, c: grammar_error(txt, typo_dict, count=c)
}

# 오타 타입 → 숫자 index 매핑
typo_variation = {
    "drop_jongsung": 1,
    "introduce_typo": 2,
    "repeat_char": 3,
    "merge_words": 4,
    "grammar_error": 5
}

# 오타 타입별로 반복
for typo_type, func in typo_funcs.items():
    save_dir = os.path.join(base_dir, typo_type)
    os.makedirs(save_dir, exist_ok=True)

    typo_idx = typo_variation[typo_type]

    for count in range(1, 6):
        output_data = []

        for idx, row in df.iterrows():
            full_query = str(row["query"])

            # "### 지문:" 기준으로 split
            if "### 지문:" not in full_query:
                continue

            pre, post = full_query.split("### 지문:", 1)
            pre = pre.strip()
            post = post.strip()

            # 오타 적용
            typo_applied = func(post, count)
            modified_query = f"{pre}\n### 지문: {typo_applied}"

            # 데이터 저장
            output_data.append({
                "id": idx,
                "query": modified_query,
                "options": eval(row.get("options", "[]")),
                "answer": row.get("answer", "")
            })

        # 저장 경로
        file_name = f"{dataset_name}_typo_{typo_idx}_level_{count}.json"
        file_path = os.path.join(save_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 저장 완료: {file_path}")
