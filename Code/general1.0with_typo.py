import os, json, difflib, ast
import pandas as pd
from typo_generation import (
    introduce_typo_to_sentence, drop_jongsung_sentence,
    jamo_repeat_typo_mixed, merge_words_typo, swap_parts_in_sentence
)

# ───── 고정 설정 ─────
csv_path = "haerae_general_knowledge.csv"
base_dir = "HAERAE1.0_GK"
dataset  = "HAERAE1.0_GK"
os.makedirs(base_dir, exist_ok=True)

typo_funcs = {
    "introduce_typo": introduce_typo_to_sentence,
    "drop_jongsung":  drop_jongsung_sentence,
    "repeat_char":    lambda t,c: jamo_repeat_typo_mixed(t, count=c, max_repeat=2),
    "merge_words":    merge_words_typo,
    "swap_parts":     swap_parts_in_sentence
}
typo_idx = {k: i+1 for i, k in enumerate(typo_funcs)}
MAX_TRY  = 20
levels   = range(1, 6)

letters_l = ["a","b","c","d","e"]
letters_u = [s.upper() for s in letters_l]

# ── helper ──────────────────────────────────────────────
def diff_pos(a,b):
    d={i for i,(x,y) in enumerate(zip(a,b)) if x!=y}
    if len(a)!=len(b):
        d.update(range(min(len(a),len(b)),max(len(a),len(b))))
    return d
def preserves(o,p,c):
    for i in diff_pos(o,p):
        if i>=len(c) or (i<len(o) and o[i]==c[i]): return False
    return True
def mutate(prev, orig, func, skip, count=1, strict=True):
    for _ in range(MAX_TRY):
        cand = func(prev, count)
        if not strict:
            return cand
        d = diff_pos(prev, cand)
        if d and d.isdisjoint(skip) and preserves(orig, prev, cand):
            skip.update(d)
            return cand
    return prev


# ────────────────────────────────────────────────────────

# ----------------------

df_orig = pd.read_csv(csv_path)

for ttype, base_func in typo_funcs.items():
    out_dir = base_dir
    os.makedirs(out_dir, exist_ok=True)
    t_id = typo_idx[ttype]
    if ttype == "introduce_typo":
        df_prev = df_orig.copy()
        for lvl in levels:
            pretty = []
            for i, row in df_orig.iterrows():  # ❗항상 원본에서 시작
                raw = str(row["question"])
                if "참고:" not in raw:
                    tgt = " ".join(raw.split())
                else:
                    pre, body = map(str.strip, raw.split("참고:", 1))
                    tgt = body if body.lower() != "nan" else pre

                # 누적 적용! → 이전 문장에 오타 추가
                prev_text = df_prev.loc[i, "question"]
                mutated = introduce_typo_to_sentence(prev_text, count=1)  # 그냥 오타 넣기

                if "참고:" not in raw:
                    q_clean = " ".join(mutated.split())
                else:
                    q_clean = " ".join((f"{pre} 참고: {mutated}" if body.lower() != "nan"
                                        else f"{mutated} 참고: {body}").split())

                # 옵션 처리
                if "options" in row and pd.notna(row["options"]):
                    opts = ast.literal_eval(row["options"])
                else:
                    opts = [row.get(col, "") for col in letters_l]
                opt_map = {letters_l[j]: opts[j] if j < len(opts) else "" for j in range(5)}

                # 정답 처리
                ans_raw = str(row.get("answer", "")).strip().lower()
                ans_letter = ans_raw.strip("()")
                if ans_letter in letters_u:
                    ans_letter = ans_letter.lower()
                elif ans_letter not in letters_l:
                    ans_letter = ""

                pretty.append({
                    "question": q_clean,
                    **opt_map,
                    "answer": ans_letter,
                    "split": row.get("split", "")
                })

                # df_prev도 업데이트해서 다음 level에 반영
                df_prev.loc[i, "question"] = q_clean

            fname = f"{dataset}_typo_{t_id}_level_{lvl}.json"
            with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                json.dump(pretty, f, ensure_ascii=False, indent=2)
            print(f"✅ {ttype} level {lvl} 저장 완료 → {fname}")


    skip_sets = [set() for _ in range(len(df_orig))]
    df_prev   = df_orig.copy()

    for lvl in levels:
        pretty=[]
        for i,row in df_prev.iterrows():
            raw=str(row["question"])
            if "참고:" not in raw:
                q_clean=" ".join(raw.split())
            else:
                pre,body=map(str.strip,raw.split("참고:",1))
                tgt=body if body.lower()!="nan" else pre
                mut = mutate(tgt, tgt, base_func, skip_sets[i], count=1, strict=(ttype not in ["repeat_char", "merge_words", "swap_parts"]))
                q_clean=" ".join((f"{pre} 참고: {mut}" if body.lower()!="nan"
                                   else f"{mut} 참고: {body}").split())
            # 옵션 뽑기
            if "options" in row and pd.notna(row["options"]):
                opts=ast.literal_eval(row["options"])
            else:
                opts=[row.get(col,"") for col in letters_l]
            opt_map={letters_l[j]: opts[j] if j<len(opts) else "" for j in range(5)}

            # answer 파싱
            ans_raw=str(row.get("answer","")).strip().lower()
            ans_letter=ans_raw.strip("()")
            if ans_letter in letters_l: pass
            elif ans_letter in letters_u: ans_letter=ans_letter.lower()
            else: ans_letter=""

            pretty.append({
                "question": q_clean,
                **opt_map,
                "answer": ans_letter,
                "split": row.get("split","")
            })

        df_prev["question"]=[r["question"] for r in pretty]

        fname=f"{dataset}_typo_{t_id}_level_{lvl}.json"
        with open(os.path.join(out_dir,fname),"w",encoding="utf-8") as f:
            json.dump(pretty,f,ensure_ascii=False,indent=2)
        print(f"✅ {ttype} level {lvl} 저장 완료 → {fname}")
