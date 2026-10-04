"use strict";

const API_BASE = "/api";
const expressionInput = document.querySelector("#expression");
const resultOutput = document.querySelector("#result");
const errorMessage = document.querySelector("#error-message");
const historyList = document.querySelector("#history-list");
const historyEmpty = document.querySelector("#history-empty");
const historyError = document.querySelector("#history-error");
const historyCount = document.querySelector("#history-count");
const historySearch = document.querySelector("#history-search");
const calculateButton = document.querySelector('[data-action="calculate"]');
let records = [];

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = !message;
}

function resetDisplay() {
  resultOutput.textContent = "—";
  showError("");
}

function insertText(value) {
  const start = expressionInput.selectionStart;
  const end = expressionInput.selectionEnd;
  expressionInput.setRangeText(value, start, end, "end");
  expressionInput.focus();
  resetDisplay();
}

function backspace() {
  const start = expressionInput.selectionStart;
  const end = expressionInput.selectionEnd;
  if (start !== end) {
    expressionInput.setRangeText("", start, end, "end");
  } else if (start > 0) {
    expressionInput.setRangeText("", start - 1, start, "end");
  }
  expressionInput.focus();
  resetDisplay();
}

async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error("无法连接服务器，请检查后端是否启动");
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error("服务器返回了无效响应");
  }
  if (!response.ok) {
    throw new Error(body.message || "请求失败，请稍后重试");
  }
  return body;
}

async function calculate() {
  const expression = expressionInput.value.trim();
  resetDisplay();
  if (!expression) {
    showError("请输入表达式");
    return;
  }
  calculateButton.disabled = true;
  calculateButton.textContent = "…";
  try {
    const body = await apiRequest("/calculate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({expression}),
    });
    resultOutput.textContent = String(body.result);
    await loadHistory();
  } catch (error) {
    showError(error.message);
  } finally {
    calculateButton.disabled = false;
    calculateButton.textContent = "=";
  }
}

function renderHistory() {
  const query = historySearch.value.trim().toLowerCase();
  const filtered = records.filter((record) => record.expression.toLowerCase().includes(query));
  historyList.replaceChildren();
  historyCount.textContent = String(records.length).padStart(2, "0");
  historyEmpty.hidden = filtered.length > 0;
  historyEmpty.innerHTML = records.length === 0
    ? "还没有计算记录。<br><span>试着输入一个表达式。</span>"
    : "没有找到匹配的记录。";
  for (const record of filtered) {
    const item = document.createElement("li");
    const detail = document.createElement("div");
    const expression = document.createElement("div");
    expression.className = "history-expression";
    expression.textContent = record.expression;
    const result = document.createElement("div");
    result.className = "history-result";
    result.textContent = `= ${record.result}`;
    const date = document.createElement("div");
    date.className = "history-meta";
    date.textContent = new Date(record.created_at).toLocaleString("zh-CN");
    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.type = "button";
    deleteButton.textContent = "删除";
    deleteButton.setAttribute("aria-label", `删除 ${record.expression} 的记录`);
    deleteButton.addEventListener("click", () => deleteRecord(record.id));
    detail.append(expression, result, date);
    item.append(detail, deleteButton);
    historyList.append(item);
  }
}

async function loadHistory() {
  try {
    records = (await apiRequest("/history")).data;
    historyError.hidden = true;
    renderHistory();
  } catch (error) {
    historyError.textContent = error.message;
    historyError.hidden = false;
  }
}

async function deleteRecord(id) {
  try {
    await apiRequest(`/history/${id}`, {method: "DELETE"});
    await loadHistory();
  } catch (error) {
    historyError.textContent = error.message;
    historyError.hidden = false;
  }
}

async function clearHistory() {
  if (!records.length || !window.confirm("确定清空全部历史记录吗？此操作无法撤销。")) return;
  try {
    await apiRequest("/history", {method: "DELETE"});
    await loadHistory();
  } catch (error) {
    historyError.textContent = error.message;
    historyError.hidden = false;
  }
}

document.querySelector(".keypad").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  if (button.dataset.key) insertText(button.dataset.key);
  if (button.dataset.action === "clear") {
    expressionInput.value = "";
    resetDisplay();
    expressionInput.focus();
  }
  if (button.dataset.action === "backspace") backspace();
  if (button.dataset.action === "calculate") calculate();
});

expressionInput.addEventListener("input", resetDisplay);
historySearch.addEventListener("input", renderHistory);
document.querySelector("#clear-history").addEventListener("click", clearHistory);
document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && document.activeElement !== historySearch) {
    event.preventDefault();
    calculate();
  } else if (event.key === "Escape") {
    expressionInput.value = "";
    resetDisplay();
    expressionInput.focus();
  } else if (event.key === "Backspace" && document.activeElement !== expressionInput && document.activeElement !== historySearch) {
    event.preventDefault();
    backspace();
  } else if (/^[0-9+*/().-]$/.test(event.key) && document.activeElement !== expressionInput && document.activeElement !== historySearch) {
    event.preventDefault();
    insertText(event.key);
  }
});

const savedTheme = localStorage.getItem("calculator-theme");
if (savedTheme === "dark") document.documentElement.dataset.theme = "dark";
document.querySelector("#theme-toggle").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme !== "dark";
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  localStorage.setItem("calculator-theme", dark ? "dark" : "light");
});

loadHistory();
