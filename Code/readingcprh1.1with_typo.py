import os
import json
import ast
import pandas as pd
from typo_generation import (
    introduce_typo_to_sentence,
    drop_jongsung_sentence,
    repeat_char_typo_no_space,
    merge_words_typo,
    swap_parts_in_sentence
)

# ───── 설정 ─────
csv_path = "haerae1.1_reading_comprehension.csv"
base_dir = "HAERAE1.1_RC"
dataset = "HAERAE1.1_RC"
os.makedirs(base_dir, exist_ok=True)

# typo 함수 매핑
typo_funcs = {
    "introduce_typo": introduce_typo_to_sentence,
    "drop_jongsung":  drop_jongsung_sentence,
    "repeat_char":    lambda t, c: repeat_char_typo_no_space(t, count=c, max_repeat=2),
    "merge_words":    merge_words_typo,
    "swap_parts":     swap_parts_in_sentence
}
typo_idx = {k: i+1 for i, k in enumerate(typo_funcs)}
MAX_TRY = 20
timeout_per_typo = 10  # 각 오타당 최대 시도 횟수
levels = range(1, 6)  # 1~5
# 레벨별 오타 비율: 5%p씩 증가
percent_map = {lvl: lvl * 0.05 for lvl in levels}
letters_l = ["a", "b", "c", "d", "e"]

# ── Helper ─────────────────────────────
def diff_pos(a, b):
    d = {i for i, (x, y) in enumerate(zip(a, b)) if x != y}
    if len(a) != len(b):
        d.update(range(min(len(a), len(b)), max(len(a), len(b))))
    return d

def preserves(o, p, c):
    for i in diff_pos(o, p):
        if i >= len(c) or (i < len(o) and o[i] == c[i]):
            return False
    return True

def mutate(prev, orig, func, skip, count=1, strict=True):
    """
    한 번만 func(prev, count) 호출해 오타를 적용합니다.
    """
    # 오타 함수에 count를 전달해 한 번만 적용
    cand = func(prev, count)
    if not strict:
        return cand
    d = diff_pos(prev, cand)
    # 충돌 없고 원본 보존 조건 만족 시 적용
    if d and d.isdisjoint(skip) and preserves(orig, prev, cand):
        skip.update(d)
        return cand
    # 조건 미달 시 원본 반환
    return prev

# ── Main ───────────────────────────────
df_orig = pd.read_csv(csv_path)

for ttype, base_func in typo_funcs.items():
    out_dir = base_dir
    os.makedirs(out_dir, exist_ok=True)
    t_id = typo_idx[ttype]

    skip_sets = [set() for _ in range(len(df_orig))]
    df_prev = df_orig.copy()

    for lvl in levels:
        pretty = []
        percentage = percent_map[lvl]

        for i in range(len(df_prev)):
            # 원본 지문 텍스트 추출
            raw_orig = str(df_orig.loc[i, "query"])
            if "### 지문:" in raw_orig:
                _, post_o = raw_orig.split("### 지문:", 1)
                if "### 질문:" in post_o:
                    passage_o, _ = post_o.split("### 질문:", 1)
                    orig_target = passage_o.strip()
                else:
                    orig_target = post_o.strip()
            else:
                orig_target = raw_orig.strip()

            # 이전 레벨 결과
            raw_prev = str(df_prev.loc[i, "query"])
            strict = False if ttype in ["repeat_char", "merge_words", "swap_parts"] else True

            # 오타 개수 계산 (원본 지문 기준)
            n_chars = len(orig_target)
            count = max(1, int(n_chars * percentage))

            # 변이 적용
            if "### 지문:" in raw_prev:
                pre, post = map(str.strip, raw_prev.split("### 지문:", 1))
                if "### 질문:" in post:
                    passage, rest = post.split("### 질문:", 1)
                    prev_passage = passage.strip()
                    mutated_passage = mutate(
                        prev_passage, orig_target, base_func,
                        skip_sets[i], count=count, strict=strict
                    )
                    q_clean = f"{pre}\n### 지문: {mutated_passage}\n### 질문: {rest.strip()}"
                else:
                    prev_post = post.strip()
                    mutated_post = mutate(
                        prev_post, orig_target, base_func,
                        skip_sets[i], count=count, strict=strict
                    )
                    q_clean = f"{pre}\n### 지문: {mutated_post}"
            else:
                prev_txt = raw_prev.strip()
                mutated = mutate(
                    prev_txt, orig_target, base_func,
                    skip_sets[i], count=count, strict=strict
                )
                q_clean = mutated

            # 옵션 및 정답 매핑
            row = df_prev.loc[i]
            opts = ast.literal_eval(row["options"])
            opt_map = {letters_l[j]: opts[j] if j < len(opts) else "" for j in range(5)}
            ans_letter = row["answer"].strip("()").lower()

            pretty.append({
                "question": q_clean,
                **opt_map,
                "answer": ans_letter
            })

            # df_prev 업데이트
            df_prev.at[i, "query"] = q_clean

        fname = f"{dataset}_typo_{t_id}_level_{lvl}.json"
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            json.dump(pretty, f, ensure_ascii=False, indent=2)
        print(f"✅ {ttype} level {lvl} 저장 완료 → {fname}")
