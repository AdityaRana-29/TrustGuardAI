/* ============================================================
   TrustGuard AI — Frontend JavaScript
   ============================================================ */

// Auto-detect: use Render backend in production, localhost in development
const IS_LOCAL = location.hostname === "localhost" || location.hostname === "127.0.0.1";
const API_BASE = IS_LOCAL
  ? "http://localhost:8000/api/v1"
  : "https://trustguard-ai-backend.onrender.com/api/v1";

// ---- Example Messages ----
const EXAMPLES = {
  scam: "Congratulations! You have won ₹25,00,000 in our lucky draw. Click here to claim your prize immediately: http://lucky-prize-india.xyz/claim. Send your bank account details and OTP to verify. Limited time offer — expires in 24 hours!",
  phishing: "Dear Customer, your SBI account has been suspended due to suspicious activity. Verify your account immediately to avoid permanent closure. Click: http://sbi-secure-update.tk/verify and enter your Net Banking ID, password and OTP.",
  fakenews: "SHOCKING: Scientists have discovered a miracle cure for diabetes that big pharma companies are hiding from the public! Doctors HATE this natural remedy. Share before it gets deleted! Government cover-up exposed — they don't want you to know the hidden truth!",
  job: "Earn ₹5000 per day from home! No experience required. Simple data entry typing job. Part time work from home. 100% guaranteed income. WhatsApp us immediately: 9876543210. Limited seats available. Act now!",
  safe: "Hi Rahul, just wanted to remind you about our team meeting tomorrow at 10 AM in the conference room. Please bring the Q3 report. Let me know if you need anything. Thanks, Priya",
};

const URL_EXAMPLES = {
  safe: "https://www.google.com",
  phish: "http://secure-bank-update.xyz/verify-account/login",
  ip: "http://192.168.1.1/banking/otp-verify",
};

// ---- Selected file for screenshot ----
let selectedFile = null;

// ============================================================
// Tab Switching
// ============================================================
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
    hideResults();
    hideURLResult();
  });
});

// ============================================================
// Character Counter
// ============================================================
const textInput = document.getElementById("text-input");
if (textInput) {
  textInput.addEventListener("input", () => {
    const count = textInput.value.length;
    document.getElementById("char-count").textContent = `${count.toLocaleString()} / 10,000`;
  });
}

// ============================================================
// Load Example Text
// ============================================================
function loadExample(type) {
  textInput.value = EXAMPLES[type] || "";
  const count = textInput.value.length;
  document.getElementById("char-count").textContent = `${count.toLocaleString()} / 10,000`;
  textInput.focus();
  hideResults();
}

function loadURLExample(type) {
  document.getElementById("url-input").value = URL_EXAMPLES[type] || "";
  hideURLResult();
}

// ============================================================
// Text Analysis
// ============================================================
async function analyzeText() {
  const text = textInput.value.trim();
  if (!text) {
    showToast("Please enter some text to analyze.", "warning");
    return;
  }
  if (text.length > 10000) {
    showToast("Text is too long. Max 10,000 characters.", "error");
    return;
  }

  showLoading();
  hideResults();

  try {
    const resp = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `Server error: ${resp.status}`);
    }

    const data = await resp.json();
    hideLoading();
    renderResults(data);
  } catch (err) {
    hideLoading();
    showToast(`Error: ${err.message}`, "error");
  }
}

// ============================================================
// URL Check
// ============================================================
async function checkURL() {
  const url = document.getElementById("url-input").value.trim();
  if (!url) {
    showToast("Please enter a URL to check.", "warning");
    return;
  }

  showLoading();
  hideURLResult();

  try {
    const resp = await fetch(`${API_BASE}/check-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `Server error: ${resp.status}`);
    }

    const data = await resp.json();
    hideLoading();
    renderURLResult(data);
  } catch (err) {
    hideLoading();
    showToast(`Error: ${err.message}`, "error");
  }
}

// ============================================================
// Screenshot Analysis
// ============================================================
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) loadImageFile(file);
}

function handleDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) loadImageFile(file);
  document.getElementById("upload-zone").classList.remove("drag-over");
}

function loadImageFile(file) {
  if (!file.type.startsWith("image/")) {
    showToast("Please upload an image file.", "warning");
    return;
  }
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById("image-preview").src = e.target.result;
    document.getElementById("image-preview-container").style.display = "block";
    document.getElementById("upload-zone").style.display = "none";
    document.getElementById("upload-footer").style.display = "flex";
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  selectedFile = null;
  document.getElementById("image-preview").src = "";
  document.getElementById("image-preview-container").style.display = "none";
  document.getElementById("upload-zone").style.display = "block";
  document.getElementById("upload-footer").style.display = "none";
  document.getElementById("file-input").value = "";
  hideResults();
}

async function analyzeScreenshot() {
  if (!selectedFile) {
    showToast("Please select an image first.", "warning");
    return;
  }

  showLoading();
  hideResults();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const resp = await fetch(`${API_BASE}/analyze-screenshot`, {
      method: "POST",
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `Server error: ${resp.status}`);
    }

    const data = await resp.json();
    hideLoading();
    renderResults(data);
  } catch (err) {
    hideLoading();
    showToast(`Error: ${err.message}`, "error");
  }
}

// ============================================================
// Render Full Results
// ============================================================
function renderResults(data) {
  const results = document.getElementById("results");
  const risk = data.risk_level; // HIGH / MEDIUM / LOW
  const riskClass = risk.toLowerCase();

  // Risk Banner
  const banner = document.getElementById("risk-banner");
  banner.className = `risk-banner ${riskClass}`;

  const icons = { HIGH: "🚨", MEDIUM: "⚠️", LOW: "✅" };
  const subtitles = {
    HIGH: "This content shows strong indicators of being a scam or misinformation.",
    MEDIUM: "This content has some suspicious elements. Exercise caution.",
    LOW: "This content appears relatively safe.",
  };

  document.getElementById("risk-icon").textContent = icons[risk] || "⚠️";
  document.getElementById("risk-title").textContent = `Risk Level: ${risk}`;
  document.getElementById("risk-subtitle").textContent = subtitles[risk] || "";
  document.getElementById("risk-badge").textContent = risk;

  // Scam Probability
  const scamProb = data.scam_probability;
  setProb("scam", scamProb, data.scam_label);

  // Fake News Probability
  const newsProb = data.fake_news_probability;
  setProb("news", newsProb, data.news_label);

  // Overall Confidence
  const conf = data.overall_confidence;
  document.getElementById("confidence-val").textContent = `${conf}%`;
  document.getElementById("confidence-val").className = `prob-value ${colorClass(conf)}`;
  setBar("confidence-bar", conf);
  document.getElementById("lang-tag").textContent = `🌐 ${data.detected_language}`;
  document.getElementById("lang-tag").className = "prob-tag tag-safe";

  // Reasons
  const reasonsList = document.getElementById("reasons-list");
  reasonsList.innerHTML = "";
  (data.reasons || []).forEach((r) => {
    const li = document.createElement("li");
    const isGood = r.toLowerCase().includes("normal") || r.toLowerCase().includes("credible") || r.toLowerCase().includes("no specific");
    li.innerHTML = `<span class="reason-icon">${isGood ? "✅" : "✓"}</span> ${r}`;
    reasonsList.appendChild(li);
  });

  // Keywords
  const keywords = data.suspicious_keywords || [];
  const kwContainer = document.getElementById("keywords-container");
  if (keywords.length > 0) {
    kwContainer.innerHTML = keywords
      .map((k) => `<span class="keyword-tag">${k}</span>`)
      .join("");
    document.getElementById("keywords-card").style.display = "block";
  } else {
    document.getElementById("keywords-card").style.display = "none";
  }

  // URL Risks
  const urlRisks = data.url_risks || [];
  if (urlRisks.length > 0) {
    const container = document.getElementById("url-risks-container");
    container.innerHTML = urlRisks.map((u) => urlRiskHTML(u)).join("");
    document.getElementById("url-risks-card").style.display = "block";
  } else {
    document.getElementById("url-risks-card").style.display = "none";
  }

  // Translated text
  if (data.translated_text) {
    document.getElementById("translated-text").textContent = data.translated_text;
    document.getElementById("translation-card").style.display = "block";
  } else {
    document.getElementById("translation-card").style.display = "none";
  }

  // Recommended Action
  document.getElementById("recommended-action").textContent = data.recommended_action || "";

  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setProb(prefix, value, label) {
  const valEl = document.getElementById(`${prefix}-prob`);
  const barEl = document.getElementById(`${prefix}-bar`);
  const tagEl = document.getElementById(`${prefix}-label`);

  valEl.textContent = `${value}%`;
  valEl.className = `prob-value ${colorClass(value)}`;
  setBar(barEl.id, value);

  const tagClass = value >= 60 ? "tag-danger" : value >= 35 ? "tag-warning" : "tag-safe";
  tagEl.textContent = label;
  tagEl.className = `prob-tag ${tagClass}`;
}

function setBar(id, value) {
  const bar = document.getElementById(id);
  bar.className = `prob-bar ${barColorClass(value)}`;
  setTimeout(() => { bar.style.width = `${Math.min(value, 100)}%`; }, 50);
}

function colorClass(value) {
  if (value >= 60) return "color-high";
  if (value >= 35) return "color-medium";
  return "color-low";
}

function barColorClass(value) {
  if (value >= 60) return "bar-high";
  if (value >= 35) return "bar-medium";
  return "bar-low";
}

function urlRiskHTML(u) {
  const riskClass = u.risk_level === "HIGH" ? "color-high" : u.risk_level === "MEDIUM" ? "color-medium" : "color-low";
  const reasons = (u.reasons || []).map((r) => `<li>${r}</li>`).join("");
  return `
    <div class="url-risk-item">
      <div class="url-risk-header">
        <span class="url-text">${escapeHTML(u.url)}</span>
        <span class="url-score ${riskClass}">Risk: ${u.risk_score}% &nbsp;|&nbsp; ${u.risk_level}</span>
      </div>
      <ul class="url-reasons">${reasons}</ul>
    </div>
  `;
}

// ============================================================
// Render URL-only Result
// ============================================================
function renderURLResult(data) {
  const section = document.getElementById("url-result");
  const banner = document.getElementById("url-risk-banner");
  const risk = data.risk_level;
  const riskClass = risk.toLowerCase();

  const icons = { HIGH: "🚨", MEDIUM: "⚠️", LOW: "✅" };
  banner.className = `risk-banner ${riskClass}`;
  banner.innerHTML = `
    <div class="risk-icon">${icons[risk] || "⚠️"}</div>
    <div class="risk-info">
      <h3>URL Risk Level: ${risk}</h3>
      <p>${escapeHTML(data.url)}</p>
    </div>
    <div class="risk-badge">${data.risk_score}%</div>
  `;

  document.getElementById("single-url-details").innerHTML = urlRiskHTML(data);
  section.classList.remove("hidden");
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// Helpers
// ============================================================
function showLoading() {
  document.getElementById("loading").classList.remove("hidden");
}
function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}
function hideResults() {
  document.getElementById("results").classList.add("hidden");
}
function hideURLResult() {
  document.getElementById("url-result").classList.add("hidden");
}

function resetForm() {
  textInput.value = "";
  document.getElementById("char-count").textContent = "0 / 10,000";
  hideResults();
  textInput.focus();
}

function resetURL() {
  document.getElementById("url-input").value = "";
  hideURLResult();
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---- Simple Toast ----
function showToast(message, type = "info") {
  const existing = document.getElementById("toast");
  if (existing) existing.remove();

  const colors = { info: "#4f8ef7", warning: "#f59e0b", error: "#ef4444" };
  const toast = document.createElement("div");
  toast.id = "toast";
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
    background: ${colors[type] || colors.info}; color: #fff;
    padding: 0.8rem 1.5rem; border-radius: 8px; font-size: 0.9rem;
    font-family: 'Inter', sans-serif; font-weight: 500;
    z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    animation: fadeIn 0.3s ease;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ---- Drag over styling ----
const uploadZone = document.getElementById("upload-zone");
if (uploadZone) {
  uploadZone.addEventListener("dragover", () => uploadZone.classList.add("drag-over"));
  uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
}
