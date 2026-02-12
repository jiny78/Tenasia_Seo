const urlInput = document.getElementById("urlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("statusText");
const scoreValue = document.getElementById("scoreValue");
const gradeValue = document.getElementById("gradeValue");
const summaryText = document.getElementById("summaryText");
const detailList = document.getElementById("detailList");
const recommendList = document.getElementById("recommendList");

const LABELS = {
  title: "\uC81C\uBAA9 \uCD5C\uC801\uD654",
  meta_description: "\uBA54\uD0C0 \uC124\uBA85",
  headings: "\uD5E4\uB529 \uAD6C\uC870",
  content: "\uBCF8\uBB38 \uD488\uC9C8",
  links: "\uB9C1\uD06C \uAD6C\uC131",
  images_alt: "\uC774\uBBF8\uC9C0 ALT",
  readability: "\uAC00\uB3C5\uC131",
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
  gradeValue.textContent = `\uB4F1\uAE09: ${grade}`;
  summaryText.textContent =
    score >= 80
      ? "\uD150\uC544\uC2DC\uC544 \uAE30\uC0AC\uC758 SEO \uAE30\uBCF8 \uAD6C\uC131\uC774 \uC591\uD638\uD569\uB2C8\uB2E4. \uCD94\uCC9C \uD56D\uBAA9 \uC911 \uC0C1\uC138 \uC774\uC288\uB97C \uBBF8\uC138 \uC870\uC815\uD574 \uBCF4\uC138\uC694."
      : "\uD150\uC544\uC2DC\uC544 \uAE30\uC0AC\uC758 SEO \uD575\uC2EC \uD56D\uBAA9\uC5D0 \uAC1C\uC120 \uC5EC\uC9C0\uAC00 \uD07D\uB2C8\uB2E4. \uAD8C\uC7A5 \uC21C\uC11C\uB300\uB85C \uC218\uC815\uD574 \uBCF4\uC138\uC694.";
}

function renderDetails(result) {
  detailList.innerHTML = "";
  const details = result.score.details ?? [];
  if (!details.length) {
    const li = document.createElement("li");
    li.textContent = "\uC138\uBD80 \uC810\uC218 \uB370\uC774\uD130\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4.";
    detailList.appendChild(li);
    return;
  }

  details.forEach((item) => {
    const li = document.createElement("li");
    li.className = "detail-item";

    const left = document.createElement("span");
    left.textContent = LABELS[item.id] ?? item.id;

    const right = document.createElement("span");
    right.className = `chip ${item.score >= item.weight * 0.75 ? "ok" : "warn"}`;
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
    li.textContent = "\uCD94\uCC9C \uD56D\uBAA9\uC774 \uC5C6\uC2B5\uB2C8\uB2E4.";
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
      "\uC81C\uBAA9 \uAE38\uC774\uB97C 50~60\uC790\uB85C \uC870\uC815\uD558\uACE0 \uD575\uC2EC \uD0A4\uC6CC\uB4DC\uB97C \uC55E\uBD80\uBD84\uC5D0 \uBC30\uCE58\uD558\uC138\uC694.",
      "\uBA54\uD0C0 \uC124\uBA85\uC744 120~160\uC790\uB85C \uBCF4\uAC15\uD558\uACE0 \uD074\uB9AD \uC720\uB3C4 \uBB38\uAD6C\uB97C \uCD94\uAC00\uD558\uC138\uC694.",
      "\uBCF8\uBB38\uC5D0 \uD150\uC544\uC2DC\uC544 \uAD00\uB828 \uB0B4\uBD80 \uAE30\uC0AC \uB9C1\uD06C\uB97C 2\uAC1C \uC774\uC0C1 \uD3EC\uD568\uD558\uC138\uC694.",
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
    setStatus("\uC62C\uBC14\uB978 URL \uD615\uC2DD\uC774 \uC544\uB2D9\uB2C8\uB2E4.");
    return;
  }

  analyzeBtn.disabled = true;
  setStatus("\uBD84\uC11D \uC911...");

  try {
    const result = await requestAnalyze(url);
    renderScore(result);
    renderDetails(result);
    renderRecommendations(result);
    setStatus("\uC644\uB8CC: \uBC31\uC5D4\uB4DC API \uACB0\uACFC\uB97C \uBC18\uC601\uD588\uC2B5\uB2C8\uB2E4.");
  } catch (_) {
    const fallback = createDemoResult(url);
    renderScore(fallback);
    renderDetails(fallback);
    renderRecommendations(fallback);
    setStatus("API \uBBF8\uC5F0\uACB0 \uC0C1\uD0DC\uC785\uB2C8\uB2E4. \uB370\uBAA8 \uACB0\uACFC\uB97C \uD45C\uC2DC\uD588\uC2B5\uB2C8\uB2E4.");
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
