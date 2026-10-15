
"use strict";

// DocuMind AI — Frontend JavaScript
const API_BASE = "http://127.0.0.1:8000";

const fileInput = document.getElementById("pdfFile");
const dropZone = document.getElementById("dropZone");
const uploadTitle = document.getElementById("uploadTitle");
const fileName = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");
const askBtn = document.getElementById("askBtn");
const analysis = document.getElementById("analysis");
const questionInput = document.getElementById("question");
const answerBox = document.getElementById("answer");
const sourcesBox = document.getElementById("sources");
const llmStatus = document.getElementById("llmStatus");
const toast = document.getElementById("toast");

let selectedFile = null;
let documentLoaded = false;

// Notifications
function showToast(message) {
  if (!toast) return;

  toast.textContent = message;
  toast.style.display = "block";

  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

// Safely insert text into HTML.
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
}

// Button loading state
function setBusy(button, busy, label) {
  if (!button) return;

  if (busy) {
    if (!button.disabled) {
      button.dataset.originalText = button.textContent;
    }

    button.textContent = label;
    button.disabled = true;
  } else {
    button.textContent =
      button.dataset.originalText || button.textContent;

    button.disabled = false;
  }
}

// Parse API responses and preserve error details.
async function parseResponse(response) {
  const raw = await response.text();
  let data = {};

  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    data = { detail: raw || response.statusText };
  }

  if (!response.ok) {
    const error = new Error(
      `HTTP ${response.status}: ${response.statusText || "Request failed"}`
    );

    error.status = response.status;
    error.responseBody = data;
    throw error;
  }

  return data;
}

function readableError(error) {
  const detail = error?.responseBody?.detail;

  if (detail) {
    return typeof detail === "string"
      ? detail
      : JSON.stringify(detail);
  }

  if (error?.name === "TypeError") {
    return (
      "The browser could not connect to the backend. " +
      "Check that FastAPI is running and that CORS allows " +
      "your frontend address. See the browser Console for details."
    );
  }

  return error?.message || "An unexpected error occurred.";
}

// PDF validation and selection
function validatePdf(file) {
  return Boolean(
    file &&
    (
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")
    )
  );
}

function chooseFile(file) {
  if (!validatePdf(file)) {
    showToast("Please choose a PDF file.");
    return;
  }

  selectedFile = file;
  documentLoaded = false;

  uploadTitle.textContent = "PDF selected";
  fileName.textContent =
    `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;

  analysis.innerHTML =
    '<p class="muted">PDF selected. Click Process Document to begin.</p>';

  answerBox.textContent = "Process the document before asking questions.";
  sourcesBox.innerHTML =
    '<p class="muted">Sources will appear after you ask a question.</p>';
}

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) {
    chooseFile(fileInput.files[0]);
  }
});

// Drag and drop
["dragenter", "dragover"].forEach(type => {
  dropZone.addEventListener(type, event => {
    event.preventDefault();
    dropZone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach(type => {
  dropZone.addEventListener(type, event => {
    event.preventDefault();
    dropZone.classList.remove("dragover");
  });
});

dropZone.addEventListener("drop", event => {
  const file = event.dataTransfer.files[0];

  if (!validatePdf(file)) {
    showToast("Please drop a PDF file.");
    return;
  }

  try {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    fileInput.files = transfer.files;
  } catch (error) {
    console.warn("Could not synchronize file input:", error);
  }

  chooseFile(file);
});

// PROCESS PDF
processBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    showToast("Choose a PDF before processing.");
    fileInput.click();
    return;
  }

  setBusy(processBtn, true, "Processing PDF…");
  documentLoaded = false;

  analysis.innerHTML = `
    <p class="muted">⏳ Uploading PDF and extracting text…</p>
    <p class="muted">
      Please wait while DocuMind AI builds the document index.
    </p>
  `;

  try {
    const form = new FormData();
    form.append("file", selectedFile);

    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: form
    });

    const data = await parseResponse(response);
    const summary = data.multimodal_summary || {};

    const pages = Number(data.pages ?? summary.pages ?? 0);
    const chunks = Number(data.chunks ?? summary.chunks ?? 0);
    const tables = Number(data.tables ?? summary.tables ?? 0);
    const images = Number(data.images ?? summary.images ?? 0);
    const ocrPages = Number(data.ocr_pages ?? summary.ocr_pages ?? 0);

    // Correct success template
    analysis.innerHTML = `
      <p class="good">
        ✓ ${escapeHtml(data.message || "Document processed successfully!")}
      </p>

      <div class="stats">
        <div class="stat">
          📄 Pages: <strong>${pages}</strong>
        </div>
        <div class="stat">
          🧩 Text chunks: <strong>${chunks}</strong>
        </div>
        <div class="stat">
          📊 Tables detected: <strong>${tables}</strong>
        </div>
        <div class="stat">
          🖼️ Images detected: <strong>${images}</strong>
        </div>
        <div class="stat">
          🔎 OCR pages: <strong>${ocrPages}</strong>
        </div>
      </div>
    `;

    documentLoaded = true;

    answerBox.textContent =
      "Document ready! Enter a question about your PDF.";

    sourcesBox.innerHTML =
      '<p class="muted">Sources will appear after you ask a question.</p>';

    showToast("Document processed successfully.");

  } catch (error) {
    console.error("PDF upload error:", error);
    console.error("API response:", error.responseBody);

    documentLoaded = false;

    analysis.innerHTML = `
      <p class="error">
        ✕ Upload failed: ${escapeHtml(readableError(error))}
      </p>
      <p class="muted">API endpoint: ${API_BASE}/upload</p>
      <p class="muted">
        Check the browser Console (F12) and FastAPI terminal.
      </p>
    `;

    showToast("PDF processing failed. Check the error details.");

  } finally {
    setBusy(processBtn, false);
  }
});

// ASK A QUESTION
askBtn.addEventListener("click", async () => {
  const question = questionInput.value.trim();

  if (!question) {
    showToast("Enter a question first.");
    questionInput.focus();
    return;
  }

  if (!documentLoaded) {
    showToast("Upload and process a PDF first.");
    return;
  }

  setBusy(askBtn, true, "Searching document…");

  answerBox.textContent =
    "Retrieving relevant passages and generating an answer…";

  sourcesBox.innerHTML =
    '<p class="muted">Loading sources…</p>';

  try {
    const response = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    const data = await parseResponse(response);

    answerBox.textContent =
      data.answer || "No answer was returned.";

    const rawSources = Array.isArray(data.sources)
      ? data.sources
      : [];

    const pages = [
      ...new Set(
        rawSources
          .map(source => {
            if (typeof source === "object" && source !== null) {
              return source.page;
            }
            return source;
          })
          .filter(page => page !== undefined && page !== null)
      )
    ];

    sourcesBox.innerHTML = pages.length
      ? pages.map(page => `
          <span class="source-chip">
            📄 Page ${escapeHtml(page)}
          </span>
        `).join("")
      : '<p class="muted">No source pages were returned.</p>';

  } catch (error) {
    console.error("Question request error:", error);
    console.error("API response:", error.responseBody);

    answerBox.textContent = readableError(error);

    sourcesBox.innerHTML =
      '<p class="muted">Sources unavailable because the request failed.</p>';

    showToast("Question request failed. Check the API and server logs.");

  } finally {
    setBusy(askBtn, false);
  }
});

// CHECK BACKEND STATUS
async function checkApi() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    await parseResponse(response);

    llmStatus.textContent =
      "FastAPI backend is online. AI requests are handled by the backend.";

    llmStatus.className = "good";

  } catch (error) {
    console.error("Backend health check failed:", error);

    llmStatus.textContent =
      `Backend unavailable at ${API_BASE}. Start FastAPI from your project folder.`;

    llmStatus.className = "error";
  }
}

checkApi();
