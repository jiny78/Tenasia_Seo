# Tenasia SEO

기사 URL을 입력받아 콘텐츠를 수집하고, SEO 점수를 산출한 뒤 개선 권장사항을 출력하는 프로젝트입니다.

## 구조
- `src/crawler.py`: 기사 수집/파싱
- `src/scorer.py`: SEO 점수 계산
- `src/recommender.py`: 개선점 추천
- `src/main.py`: 단일 URL 분석 실행
- `src/batch_report.py`: URL 목록 일괄 분석 리포트 생성
- `web/index.html`: SEO 대시보드 UI
- `configs/rubric.v1.json`: 점수 기준

## 사이트(프론트) 실행
`web/index.html`을 브라우저로 열면 바로 UI를 확인할 수 있습니다.

백엔드 API(`/api/analyze`)가 연결되지 않은 경우:
- 화면은 자동으로 데모 결과를 표시합니다.

## Streamlit (실시간 연동)
현재 프로젝트는 Streamlit 앱에서 `crawler -> scorer -> recommender`를 직접 호출합니다.
즉, URL 입력 시 실시간으로 크롤링 후 점수/추천을 표시합니다.

실행:
```powershell
streamlit run streamlit_app.py
```

Auto refresh:
- 사이드바에서 `Auto refresh every 60s` 체크 시 60초마다 재분석합니다.

## 실행
```powershell
python -m src.main --url "https://example.com/article"
```

## 배치 리포트
1. `data/samples/urls.txt`에 분석 URL을 한 줄씩 입력
2. 아래 실행

```powershell
python -m src.batch_report --url-file data/samples/urls.txt --output data/reports/sample_report.json
```

## 테스트
```powershell
python -m pytest -q
```

## Git Push
```powershell
git add .
git commit -m "feat: streamlit live analyzer integration"
git push -u origin work
```

## Streamlit Cloud 배포
1. GitHub에 현재 브랜치를 push
2. https://share.streamlit.io 접속 후 GitHub repo 선택
3. Main file path: `streamlit_app.py`
4. Deploy 클릭

배포 후 URL에서 바로 온라인 사용 가능합니다.

## 다음 단계
1. Tenasia 기사 DOM 패턴에 맞는 선택자 보정
2. 키워드 기반 세부 점수(제목-본문 일치도) 추가
3. 추천 문구에 예상 영향도(트래픽/CTR) 추정치 추가
