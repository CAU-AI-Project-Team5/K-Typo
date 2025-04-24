import hgtk
import random
import re

# ========================================
# 오타 맵 정의
# ========================================

typo_map_choseong = {
    'ㄱ': ['ㄷ', 'ㅅ'], 'ㄴ': ['ㄷ', 'ㅇ'], 'ㄷ': ['ㅇ', 'ㅈ'], 'ㄹ': ['ㅇ', 'ㅎ'],
    'ㅁ': ['ㄴ', 'ㅂ'], 'ㅂ': ['ㅈ', 'ㅁ'], 'ㅅ': ['ㄱ', 'ㅎ'], 'ㅇ': ['ㄴ', 'ㄹ'],
    'ㅈ': ['ㅂ', 'ㄷ'], 'ㅊ': ['ㅌ', 'ㅍ'], 'ㅋ': ['ㅌ', 'ㅁ'], 'ㅌ': ['ㅋ', 'ㅊ'],
    'ㅍ': ['ㅊ', 'ㄹ'], 'ㅎ': ['ㄹ', 'ㅊ'],
}
typo_map_jungseong = {
    'ㅏ': ['ㅑ', 'ㅓ'], 'ㅑ': ['ㅕ', 'ㅐ'], 'ㅓ': ['ㅗ', 'ㅏ'], 'ㅕ': ['ㅛ', 'ㅑ'],
    'ㅗ': ['ㅓ', 'ㅜ'], 'ㅛ': ['ㅗ', 'ㅕ'], 'ㅜ': ['ㅗ', 'ㅡ'], 'ㅠ': ['ㅗ', 'ㅜ'],
    'ㅡ': ['ㅜ', 'ㅏ'], 'ㅣ': ['ㅏ', 'ㅐ'], 'ㅐ': ['ㅑ', 'ㅔ'], 'ㅔ': ['ㅐ', 'ㅣ'],
}
typo_map_jongseong = {
    'ㄱ': ['ㄴ', 'ㅅ', 'ㄹ'], 'ㄲ': ['ㄱ', 'ㅅ'], 'ㄳ': ['ㄱ', 'ㅅ'], 'ㄴ': ['ㅇ', 'ㄵ'],
    'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'], 'ㄷ': ['ㅌ', 'ㅅ'], 'ㄹ': ['ㄱ', 'ㅁ', 'ㅂ'],
    'ㄺ': ['ㄹ', 'ㄱ'], 'ㄻ': ['ㄹ', 'ㅁ'], 'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'],
    'ㄾ': ['ㄹ', 'ㅌ'], 'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'], 'ㅁ': ['ㄴ', 'ㅇ'],
    'ㅂ': ['ㅁ', 'ㅄ'], 'ㅄ': ['ㅂ', 'ㅅ'], 'ㅅ': ['ㄱ', 'ㅈ'], 'ㅆ': ['ㅅ'], 'ㅇ': ['ㅁ', 'ㄴ'],
    'ㅈ': ['ㅅ', 'ㅊ'], 'ㅊ': ['ㅈ', 'ㅋ'], 'ㅋ': ['ㅊ', 'ㅌ'], 'ㅌ': ['ㅋ', 'ㅍ'],
    'ㅍ': ['ㅌ', 'ㅎ'], 'ㅎ': ['ㅍ', 'ㅀ'],
}

typo_dict = {
    "안": "않", "않": "안", "되": "돼", "돼": "되", "낫": "낳", "낳": "낫", "났": "낫",
    "너무": "넘", "뭐": "머", "그렇다": "글타", "하여튼": "하튼", "하여간": "하튼",
    "어떻게": "어케", "예쁘다": "이쁘다", "오랫동안": "오랜동안", "왠지": "웬지",
    "웬일이니": "왠일이니", "잠그다": "잠구다", "젖히다": "제끼다", "찌개": "찌게",
    "통째로": "통채로", "가엾다": "가엽다", "거꾸로": "꺼꾸로", "구레나룻": "구렛나루",
    "굵다랗다": "굵따랗다", "깍쟁이": "깍정이", "꼬라지": "꼬나지", "나부랭이": "나부랑이",
    "나지막이": "나즈막이", "너부죽이": "너부죽히", "놀래다": "놀래키다",
    "느지막이": "느즈막이", "다디달다": "다디닳다", "다붓이": "다부지게",
    "다사스럽다": "다사하다", "닦달하다": "닥달하다", "대증요법": "대중요법",
    "덮이다": "덮히다", "돌멩이": "돌맹이", "되뇌다": "되뇌이다",
    "둘러싸이다": "둘러쌓이다", "딴기적다": "딴기쩍다", "떠벌리다": "떠벌이다",
    "떼려야": "떼래야",
}

def get_typo_indices(text, count=None, ratio=None, filter_fn=lambda c: True):
    """
    ratio로 들어와도 count로 환산하고,
    filter_fn에 맞는 문자 인덱스 중 max count만큼 뽑아서 반환.
    """
    # 공백 포함한 전체 길이 기준으로 count 계산
    if count is None and ratio is not None:
        count = max(1, int(len(text) * ratio))
    elif count is None:
        count = 0

    # 오타를 적용할 수 있는 문자 인덱스만 추림
    valid_indices = [i for i, c in enumerate(text) if filter_fn(c)]
    if not valid_indices:
        return []

    # count가 인덱스 수보다 많으면 가능한 만큼만
    selected_count = min(count, len(valid_indices))
    return random.sample(valid_indices, selected_count)


# ========================================
# 오타 삽입 함수들
# ========================================

def introduce_typo_to_char(char):
    try:
        cho, jung, jong = hgtk.letter.decompose(char)
        target = random.choice(['cho', 'jung', 'jong'])
        if target == 'cho' and cho in typo_map_choseong:
            cho = random.choice(typo_map_choseong[cho])
        elif target == 'jung' and jung in typo_map_jungseong:
            jung = random.choice(typo_map_jungseong[jung])
        elif target == 'jong' and jong in typo_map_jongseong:
            jong = random.choice(typo_map_jongseong[jong])
        return hgtk.letter.compose(cho, jung, jong)
    except:
        return char

def introduce_typo_to_sentence(text, count=None, ratio=None, skip_indices=None):
    if skip_indices is None:
        skip_indices = set()

    # 새로운 typo를 적용할 수 있는 인덱스 계산
    def is_valid_char(c):
        return hgtk.checker.is_hangul(c)

    # skip_indices를 제외한 후보군만 넘김
    indices = get_typo_indices(
        text,
        count,
        ratio,
        filter_fn=lambda c: is_valid_char(c)
    )
    indices = [i for i in indices if i not in skip_indices]

    result = list(text)
    for i in indices:
        result[i] = introduce_typo_to_char(result[i])
    return ''.join(result), indices  # ✅ 적용된 인덱스를 반환하면 이후 level에서도 추적 가능


def drop_jongsung_char(char):
    try:
        cho, jung, jong = hgtk.letter.decompose(char)
        return hgtk.letter.compose(cho, jung, '') if jong else char
    except:
        return char

def drop_jongsung_sentence(text, count=None, ratio=None):
    # 종성이 있는 한글 음절만 필터링
    def has_jongsung(c):
        try:
            cho, jung, jong = hgtk.letter.decompose(c)
            return bool(jong)
        except:
            return False

    indices = get_typo_indices(text, count, ratio, has_jongsung)
    result = list(text)
    for i in indices:
        result[i] = drop_jongsung_char(result[i])
    return ''.join(result)

def repeat_char_typo_no_space(text, count=None, ratio=None, max_repeat=2):
    # 조건: 한글이고, 공백 아니고, 기호도 아닌 문자만
    def is_repeatable_korean_char(c):
        return hgtk.checker.is_hangul(c) and c not in [':', '.', ',', '?', '!', '-', '—', '~', '…']

    # 반복되는 문자 위치 추출 → 제외
    repeated_chars = set()
    for match in re.finditer(r'(.)\1{1,}', text):  # 연속으로 같은 글자가 2번 이상 나올 때
        repeated_chars.update(match.group(0))  # "ㅋㅋㅋ" → 'ㅋ'을 제외

    def filter_fn(c):
        return is_repeatable_korean_char(c) and c not in repeated_chars

    indices = get_typo_indices(text, count, ratio, filter_fn)
    result = list(text)
    for i in indices:
        result[i] = result[i] * random.randint(2, max_repeat)
    return ''.join(result)


def merge_words_typo(text, count=None, ratio=None):
    indices = get_typo_indices(text, count, ratio, lambda c: c == ' ')
    result = list(text)
    for i in indices:
        result[i] = ''
    return ''.join(result)

def grammar_error(text, typo_dict, count=None, ratio=None):
    typo_candidates = [(k, v) for k, v in typo_dict.items() if re.search(rf'\b{k}\b', text)]
    if not typo_candidates:
        return text
    if count is not None:
        n = min(count, len(typo_candidates))
    elif ratio is not None:
        n = max(1, int(len(typo_candidates) * ratio))
    else:
        n = 0
    selected = random.sample(typo_candidates, n)
    for correct, typo in selected:
        text = re.sub(rf'\b{correct}\b', typo, text, count=1)
    return text

def swap_parts_in_char(char):
    try:
        # 완성된 한글 음절인지 확인 (예: '강'은 True, 'ㅏ'나 'ㄱ'은 False)
        if not hgtk.letter.is_complete_syllable(char):
            return char

        cho, jung, jong = hgtk.letter.decompose(char)

        # 종성이 있으면: cho + jong + jung
        # 종성이 없으면: jung + cho
        if jong:
            return cho + jong + jung
        else:
            return jung + cho
    except:
        return char


def swap_parts_in_sentence(text, count=None, ratio=None):
    indices = get_typo_indices(text, count, ratio, hgtk.checker.is_hangul)
    result = list(text)
    for i in indices:
        result[i] = swap_parts_in_char(result[i])
    return ''.join(result)
