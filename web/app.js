const urlInput = document.getElementById("urlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("statusText");
const scoreValue = document.getElementById("scoreValue");
const gradeValue = document.getElementById("gradeValue");
const summaryText = document.getElementById("summaryText");
const detailList = document.getElementById("detailList");
const recommendList = document.getElementById("recommendList");

const LABELS = {
  title: "Title",
  meta_description: "Meta Description",
  headings: "Headings",
  content: "Content",
  links: "Links",
  images_alt: "Image Alt",
  readability: "Readability",
};

function setStatus(message) {
  statusText.textContent = message;
}

function validateUrl(value) {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch (_) {
    return false;
  }
}

function renderScore(result) {
  const score = Math.round(result.score.total_score ?? 0);
  const grade = result.score.grade ?? "-";
  scoreValue.textContent = String(score);
  gradeValue.textContent = `등급: ${grade}`;
  summaryText.textContent = score >= 80
    ? "기본 SEO 품질이 양호합니다. 추천 항목 중심으로 미세 조정하세요."
    : "핵심 SEO 항목의 점수 손실이 큽니다. 추천 우선순위부터 수정하세요.";
}

function renderDetails(result) {
  detailList.innerHTML = "";
  const details = result.score.details ?? [];
  if (!details.length) {
    const li = document.createElement("li");
    li.textContent = "세부 점수 데이터가 없습니다.";
    detailList.appendChild(li);
    return;
  }

  details.forEach((item) => {
    const li = document.createElement("li");
    li.className = "detail-item";

    const left = document.createElement("span");
    left.textContent = LABELS[item.id] ?? item.id;

    const right = document.createElement("span");
    right.className = "chip " + (item.score >= item.weight * 0.75 ? "ok" : "warn");
    right.textContent = `${Math.round(item.score)}/${item.weight}`;

    li.append(left, right);
    detailList.appendChild(li);
  });
}

function renderRecommendations(result) {
  recommendList.innerHTML = "";
  const recommendations = result.recommendations ?? [];
  if (!recommendations.length) {
    const li = document.createElement("li");
    li.textContent = "추천 항목이 없습니다.";
    recommendList.appendChild(li);
    return;
  }
  recommendations.forEach((message) => {
    const li = document.createElement("li");
    li.textContent = message;
    recommendList.appendChild(li);
  });
}

function createDemoResult(url) {
  return {
    url,
    score: {
      total_score: 68,
      grade: "D",
      details: [
        { id: "title", score: 12, weight: 20 },
        { id: "meta_description", score: 6, weight: 15 },
        { id: "headings", score: 11, weight: 15 },
        { id: "content", score: 12, weight: 20 },
        { id: "links", score: 5, weight: 10 },
        { id: "images_alt", score: 9, weight: 10 },
        { id: "readability", score: 13, weight: 10 },
      ],
    },
    recommendations: [
      "제목 길이를 50~60자로 조정하고 핵심 키워드를 앞부분에 배치하세요.",
      "메타 설명을 120~160자로 보강해 클릭 유도 문구를 추가하세요.",
      "본문 내 내부 링크 2개 이상, 외부 신뢰 출처 1개 이상을 포함하세요.",
    ],
  };
}

async function requestAnalyze(url) {
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

async function onAnalyze() {
  const url = urlInput.value.trim();
  if (!validateUrl(url)) {
    setStatus("올바른 URL 형식이 아닙니다.");
    return;
  }

  analyzeBtn.disabled = true;
  setStatus("분석 중...");

  try {
    const result = await requestAnalyze(url);
    renderScore(result);
    renderDetails(result);
    renderRecommendations(result);
    setStatus("완료: 백엔드 API 결과를 반영했습니다.");
  } catch (_) {
    const fallback = createDemoResult(url);
    renderScore(fallback);
    renderDetails(fallback);
    renderRecommendations(fallback);
    setStatus("API 미연결 상태입니다. 데모 결과를 표시했습니다.");
  } finally {
    analyzeBtn.disabled = false;
  }
}

analyzeBtn.addEventListener("click", onAnalyze);
urlInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    onAnalyze();
  }
});
