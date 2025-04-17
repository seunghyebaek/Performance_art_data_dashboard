import re

def cleanText(raw_text: str) -> str:
    # **별표 제거
    text = re.sub(r"\*\*", "", raw_text)
    # \n 문자열을 실제 줄바꿈 문자로 변환
    text = text.replace("\\n", "\n")
    # 앞뒤 공백 제거
    return text.strip()