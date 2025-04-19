import hgtk
import random
import re


# 초성/중성 오타 맵
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
    'ㄱ': ['ㄴ', 'ㅅ', 'ㄹ'], 'ㄲ': ['ㄱ', 'ㅅ'],
    'ㄳ': ['ㄱ', 'ㅅ'], 'ㄴ': ['ㅇ', 'ㄵ'], 'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'],
    'ㄷ': ['ㅌ', 'ㅅ'], 'ㄹ': ['ㄱ', 'ㅁ', 'ㅂ'], 'ㄺ': ['ㄹ', 'ㄱ'], 'ㄻ': ['ㄹ', 'ㅁ'],
    'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'], 'ㄾ': ['ㄹ', 'ㅌ'], 'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'],
    'ㅁ': ['ㄴ', 'ㅇ'], 'ㅂ': ['ㅁ', 'ㅄ'], 'ㅄ': ['ㅂ', 'ㅅ'], 'ㅅ': ['ㄱ', 'ㅈ'], 'ㅆ': ['ㅅ'],
    'ㅇ': ['ㅁ', 'ㄴ'], 'ㅈ': ['ㅅ', 'ㅊ'], 'ㅊ': ['ㅈ', 'ㅋ'], 'ㅋ': ['ㅊ', 'ㅌ'],
    'ㅌ': ['ㅋ', 'ㅍ'], 'ㅍ': ['ㅌ', 'ㅎ'], 'ㅎ': ['ㅍ', 'ㅀ'],
}




# 맞춤법 대체 맵
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


# 초성/중성/종성 오타
def introduce_typo_to_char(char):
    try:
        cho, jung, jong = hgtk.letter.decompose(char)
        target = random.choice(['cho', 'jung', 'jong'])  # 어떤 부분에 오타 넣을지 선택


        if target == 'cho' and cho in typo_map_choseong:
            cho = random.choice(typo_map_choseong[cho])
        elif target == 'jung' and jung in typo_map_jungseong:
            jung = random.choice(typo_map_jungseong[jung])
        elif target == 'jong' and jong in typo_map_jongseong:
            jong = random.choice(typo_map_jongseong[jong])


        return hgtk.letter.compose(cho, jung, jong)
    except (hgtk.exception.NotHangulException, hgtk.exception.NotLetterException):
        return char




def introduce_typo_to_sentence(text, count):
    hangul_indices = [i for i, c in enumerate(text) if hgtk.checker.is_hangul(c)]
    selected_indices = random.sample(hangul_indices, min(count, len(hangul_indices)))
    result = list(text)
    for idx in selected_indices:
        result[idx] = introduce_typo_to_char(result[idx])
    return ''.join(result)




# 종성 생략
def drop_jongsung_char_fixed(char):
    try:
        cho, jung, jong = hgtk.letter.decompose(char)
        if jong != '':
            return hgtk.letter.compose(cho, jung, '')
        return char
    except (hgtk.exception.NotHangulException, hgtk.exception.NotLetterException):
        return char


def drop_jongsung_sentence(text, count):
    hangul_indices = [i for i, c in enumerate(text) if hgtk.checker.is_hangul(c)]
    selected_indices = random.sample(hangul_indices, min(count, len(hangul_indices)))
    result = list(text)
    for idx in selected_indices:
        result[idx] = drop_jongsung_char_fixed(result[idx])
    return ''.join(result)




# 글자 중복
def repeat_char_typo_no_space(text, count, max_repeat):
    hangul_indices = [i for i, c in enumerate(text) if c != ' ']
    selected_indices = random.sample(hangul_indices, min(count, len(hangul_indices)))
    result = list(text)
    for idx in selected_indices:
        repeat_times = random.randint(2, max_repeat)
        result[idx] = result[idx] * repeat_times
    return ''.join(result)




# 띄어쓰기 생략
def merge_words_typo(text, count):
    space_indices = [i for i, c in enumerate(text) if c == ' ']
    if not space_indices:
        return text  # 더 이상 생략할 띄어쓰기가 없으면 그대로 반환
    selected_indices = random.sample(space_indices, min(count, len(space_indices)))
    result = list(text)
    for idx in selected_indices:
        result[idx] = ''  # 띄어쓰기 생략
    return ''.join(result)


# 맞춤법 오류 대체
def grammar_error(text, typo_dict, count):
    typo_candidates = [(correct, typo) for correct, typo in typo_dict.items() if re.search(rf'\b{correct}\b', text)]
    if not typo_candidates:
        return text  # 더 이상 적용할 맞춤법 오류가 없으면 그대로 반환


    selected_candidates = random.sample(typo_candidates, min(count, len(typo_candidates)))
    for correct, typo in selected_candidates:
        text = re.sub(rf'\b{correct}\b', typo, text, count=1)
    return text
