from typing import Any, Dict, List, Tuple


BASE_MESSAGES = {
    "title_missing": "제목이 없습니다. 핵심 인물과 사건이 보이도록 제목을 작성하세요.",
    "title_too_short": "제목이 짧습니다. 인물명과 핵심 포인트를 함께 넣어 보강하세요.",
    "title_too_long": "제목이 깁니다. 중복 표현을 줄이고 핵심 정보만 남기세요.",
    "title_not_ideal_length": "제목 길이를 조금 조정하면 노출 안정성이 좋아집니다.",
    "meta_description_missing": "메타 설명이 없습니다. 기사 핵심을 두 문장으로 요약해 넣으세요.",
    "meta_description_too_short": "메타 설명이 짧습니다. 핵심 정보와 클릭 유도 문구를 보강하세요.",
    "meta_description_too_long": "메타 설명이 깁니다. 핵심 정보 위주로 줄이세요.",
    "meta_description_not_ideal_length": "메타 설명 길이를 조금 조정하세요.",
    "h1_missing": "H1이 없습니다. 기사 주제를 한 줄로 요약한 H1을 추가하세요.",
    "h1_missing_soft": "H1이 없지만 제목이 명확합니다. 필요하면 H1 한 줄만 보강하세요.",
    "h2_insufficient": "소제목 H2가 부족합니다. 문맥 전환 지점에 소제목을 넣으세요.",
    "content_too_short": "본문이 짧습니다. 핵심 사실과 맥락 정보를 보강하세요.",
    "content_below_ideal_length": "본문 분량을 조금 보강하면 검색 가시성이 더 좋아집니다.",
    "content_missing_subject": "본문의 주체 정보가 약합니다. 인물이나 팀명을 명확히 넣으세요.",
    "content_missing_event": "본문의 사건 정보가 약합니다. 무엇이 있었는지 명확히 적으세요.",
    "content_missing_time_context": "본문의 시점 맥락이 약합니다. 날짜나 시점을 보강하세요.",
    "internal_links_insufficient": "내부 링크가 부족합니다. 관련 기사 링크를 추가하세요.",
    "images_missing_alt": "이미지 alt가 누락되었습니다. 이미지 설명을 alt에 입력하세요.",
    "sentences_too_short": "문장이 지나치게 짧습니다. 의미 단위로 묶어 흐름을 보강하세요.",
    "sentences_too_long": "문장이 깁니다. 핵심 문장과 보조 문장으로 분리하세요.",
    "sentence_length_not_ideal": "문장 길이 균형을 맞추면 읽기 흐름이 좋아집니다.",
}

ENTERTAINMENT_MESSAGES = {
    "h2_insufficient": "연예 단신과 포토 기사에서는 H2가 없어도 됩니다. 심층형 기사에서만 H2를 권장합니다.",
    "content_too_short": "연예 단신 기사일 수 있습니다. 분량보다 핵심 사실 삼요소를 먼저 보강하세요.",
    "content_below_ideal_length": "연예 기사 톤을 유지하면서 배경 맥락 문단 하나만 추가해도 충분합니다.",
}

BASE_EXAMPLES = {
    "title_too_short": "수정 예시: 인물명과 핵심 이벤트를 제목 앞부분에 배치",
    "meta_description_missing": "수정 예시: 일정과 콘셉트와 관전 포인트를 두 문장으로 요약",
    "h2_insufficient": "수정 예시: H2 하나는 핵심 포인트, 하나는 현장 반응으로 구성",
    "content_too_short": "수정 예시: 배경 설명 한 문단과 인용 한 문단 추가",
    "content_missing_subject": "수정 예시: 첫 문장에 인물명 또는 팀명을 명시",
    "content_missing_event": "수정 예시: 발표, 공개, 출연 같은 핵심 사건 문장을 명시",
    "content_missing_time_context": "수정 예시: 오늘, 지난, 방송일 같은 시점 문구 추가",
    "internal_links_insufficient": "수정 예시: 관련 기사 1~2건 내부 링크 삽입",
}

ENTERTAINMENT_EXAMPLES = {
    "h2_insufficient": "Example: Use H2 only for deep-dive pieces.",
    "content_too_short": "Example: 3 lines facts, 2 lines reactions, 1 line next schedule.",
    "content_below_ideal_length": "Example: Keep tone and add one short context paragraph.",
}


def _priority(item: Dict[str, Any]) -> float:
    return float(item.get("weight", 0)) - float(item.get("score", 0))


def _profile_domain(score_result: Dict[str, Any]) -> str:
    return (score_result.get("profile") or {}).get("domain", "general_news")


def _message(issue: str, domain: str) -> str:
    if domain == "entertainment_news" and issue in ENTERTAINMENT_MESSAGES:
        return ENTERTAINMENT_MESSAGES[issue]
    return BASE_MESSAGES.get(issue, "")


def _example(issue: str, domain: str) -> str:
    if domain == "entertainment_news" and issue in ENTERTAINMENT_EXAMPLES:
        return ENTERTAINMENT_EXAMPLES[issue]
    return BASE_EXAMPLES.get(issue, "")


def _collect_issue_actions(details: List[Dict[str, Any]], domain: str) -> List[Tuple[float, str]]:
    actions: List[Tuple[float, str]] = []
    for item in details:
        gap = _priority(item)
        if gap <= 0:
            continue
        for issue in item.get("issues", []):
            msg = _message(issue, domain)
            if not msg:
                continue
            ex = _example(issue, domain)
            full = f"{msg}\n{ex}" if ex else msg
            actions.append((gap, full))
    return actions


def recommend_fixes(score_result: Dict[str, Any], max_items: int = 8) -> List[str]:
    if score_result.get("error"):
        return ["크롤링 오류를 먼저 해결하세요. URL 접근 가능 여부와 응답 상태 코드를 확인하세요."]

    domain = _profile_domain(score_result)
    details = score_result.get("details", [])
    actions = _collect_issue_actions(details, domain)
    actions.sort(key=lambda pair: pair[0], reverse=True)

    deduped: List[str] = []
    seen = set()
    for _, message in actions:
        if message in seen:
            continue
        seen.add(message)
        deduped.append(message)
        if len(deduped) >= max_items:
            break

    if deduped:
        return deduped

    if domain == "entertainment_news":
        return ["연예 기사 특성에 맞는 SEO 기준을 충족했습니다. 제목과 요약문만 미세 조정하세요."]
    return ["주요 SEO 항목이 기준을 충족했습니다. 제목과 요약문만 추가 점검하세요."]
