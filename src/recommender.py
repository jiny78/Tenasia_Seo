from typing import Any, Dict, List, Tuple


ISSUE_MESSAGES = {
    "title_missing": "제목이 없습니다. 핵심 키워드를 포함해 50~60자 내로 작성하세요.",
    "title_too_short": "제목이 짧습니다. 검색 의도를 반영해 50~60자 범위로 확장하세요.",
    "title_too_long": "제목이 깁니다. 60자 내외로 압축해 CTR 저하를 방지하세요.",
    "title_not_ideal_length": "제목 길이를 50~60자로 조정하면 검색 결과 노출이 안정적입니다.",
    "meta_description_missing": "메타 설명이 없습니다. 120~160자로 핵심 요약과 클릭 유도 문구를 넣으세요.",
    "meta_description_too_short": "메타 설명이 짧습니다. 핵심 정보와 행동 유도 문구를 보강하세요.",
    "meta_description_too_long": "메타 설명이 깁니다. 160자 내외로 줄여 잘림을 방지하세요.",
    "meta_description_not_ideal_length": "메타 설명 길이를 120~160자로 맞추세요.",
    "h1_missing": "H1이 없습니다. 기사 주제를 한 줄로 정의하는 H1을 1개 추가하세요.",
    "h2_insufficient": "H2 소제목이 부족합니다. 문맥 전환 지점마다 H2를 최소 2개 이상 사용하세요.",
    "content_too_short": "본문이 짧습니다. 핵심 맥락, 근거, 예시를 보강해 분량을 확장하세요.",
    "content_below_ideal_length": "본문 분량을 보강하면 경쟁 문서 대비 가시성이 더 높아집니다.",
    "internal_links_insufficient": "내부 링크가 부족합니다. 관련 기사/태그 페이지를 2개 이상 연결하세요.",
    "external_links_missing": "외부 링크는 필수 항목이 아닙니다. 텐아시아 내부 링크 구조에 집중하세요.",
    "images_missing_alt": "이미지 alt 텍스트가 누락되었습니다. 모든 이미지에 설명형 alt를 작성하세요.",
    "readability_not_measurable": "가독성 분석이 불가합니다. 문장 단위 본문 텍스트를 확보하세요.",
    "sentences_too_short": "문장이 지나치게 짧습니다. 문맥이 끊기지 않게 문장을 적절히 확장하세요.",
    "sentences_too_long": "문장이 길어 가독성이 떨어집니다. 문장을 2~3개로 분리하세요.",
    "sentence_length_not_ideal": "평균 문장 길이를 12~25단어 범위로 조정하세요.",
}

ISSUE_EXAMPLES = {
    "title_missing": "수정 예시: [수정 전] 제목 없음 -> [수정 후] 아이돌 A, 신곡 첫 무대 비하인드 공개",
    "title_too_short": "수정 예시: [수정 전] 컴백 소식 -> [수정 후] 아이돌 A, 9개월 만에 컴백...타이틀곡 첫 티저 공개",
    "title_too_long": "수정 예시: [수정 전] 지나치게 긴 제목(70자+) -> [수정 후] 핵심 정보 중심 55자 내 제목",
    "meta_description_missing": "수정 예시: [수정 후] 신곡 포인트·무대 관전 요소를 2문장으로 요약해 클릭 유도",
    "meta_description_too_short": "수정 예시: [수정 전] 컴백했다 -> [수정 후] 신곡 콘셉트와 관전 포인트를 130자로 요약",
    "meta_description_too_long": "수정 예시: [수정 전] 200자 이상 설명 -> [수정 후] 핵심만 남긴 140자 설명",
    "h1_missing": "수정 예시: [수정 후] H1: 아이돌 A, 컴백 쇼케이스 현장 공개",
    "h2_insufficient": "수정 예시: [수정 후] H2 1) 신곡 포인트 2) 무대·스타일링 관전 포인트",
    "content_too_short": "수정 예시: [수정 후] 배경 설명 + 인터뷰 인용 + 팬 반응 문단 추가",
    "content_below_ideal_length": "수정 예시: [수정 후] 핵심 장면/인용/맥락 문단 2개 추가",
    "internal_links_insufficient": "수정 예시: [수정 후] 관련 기사 2건(컴백 기사, 인터뷰 기사) 내부 링크 삽입",
    "images_missing_alt": "수정 예시: [수정 후] alt='아이돌 A 쇼케이스 포토월 현장'",
    "sentences_too_short": "수정 예시: [수정 후] 단문 3개를 연결해 맥락 있는 1~2문장으로 통합",
    "sentences_too_long": "수정 예시: [수정 후] 긴 문장을 사실/해설 문장으로 분리",
    "sentence_length_not_ideal": "수정 예시: [수정 후] 핵심문 1개 + 보충문 1개 구성으로 문장 길이 균형 조정",
}


def _priority(item: Dict[str, Any]) -> float:
    return float(item.get("weight", 0)) - float(item.get("score", 0))


def _collect_issue_actions(details: List[Dict[str, Any]]) -> List[Tuple[float, str]]:
    actions: List[Tuple[float, str]] = []
    for item in details:
        gap = _priority(item)
        if gap <= 0:
            continue
        for issue in item.get("issues", []):
            message = ISSUE_MESSAGES.get(issue)
            if not message:
                continue
            example = ISSUE_EXAMPLES.get(issue)
            full_message = f"{message}\n{example}" if example else message
            actions.append((gap, full_message))
    return actions


def recommend_fixes(score_result: Dict[str, Any], max_items: int = 8) -> List[str]:
    if score_result.get("error"):
        return [
            "크롤링 오류를 먼저 해결하세요. URL 접근 가능 여부, robots 정책, 응답 상태코드를 확인해야 합니다."
        ]

    details = score_result.get("details", [])
    actions = _collect_issue_actions(details)
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

    return ["주요 SEO 항목이 기준을 충족했습니다. 제목·메타 설명만 A/B 테스트로 미세 조정해 보세요."]
