const API_URL = "http://127.0.0.1:8000/api";

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusBadge = document.getElementById("status-badge");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const statusMsg = document.getElementById("statusMsg");
const wpmSlider = document.getElementById("wpmSlider");
const wpmValue = document.getElementById("wpmValue");
const docInput = document.getElementById("docKey");
const sourceInput = document.getElementById("sourceText");
const cleanupToggle = document.getElementById("cleanupToggle");

// Slider Update
wpmSlider.addEventListener("input", (e) => {
    wpmValue.innerText = e.target.value;
});

// Toast
function showToast(msg, type = "info") {
    const toast = document.getElementById("toast");
    toast.innerText = msg;
    toast.className = `fixed bottom-5 right-5 px-4 py-2 rounded-lg shadow-lg transform transition-transform duration-300 text-sm z-50 ${type === "error" ? "bg-red-900 border-red-700 border text-white" :
            type === "success" ? "bg-green-900 border-green-700 border text-white" :
                "bg-gray-800 border-gray-600 border text-white"
        }`;
    toast.style.transform = "translateY(0)";
    setTimeout(() => {
        toast.style.transform = "translateY(5rem)";
    }, 3000);
}

async function login() {
    try {
        showToast("Launching browser...", "info");
        await fetch(`${API_URL}/login`, { method: "POST" });
        showToast("Browser launched. Please log in.", "success");
    } catch (e) {
        showToast("Failed to launch login browser", "error");
    }
}


async function startTyping() {
    const url = docInput.value;
    const text = sourceInput.value;
    const wpm = parseInt(wpmSlider.value);
    const cleanup = cleanupToggle.checked;

    if (!url) {
        showToast("Please enter a Google Doc URL", "error");
        return;
    }
    if (!text) {
        showToast("Please enter some text to type", "error");
        return;
    }

    // Disable button
    startBtn.disabled = true;
    startBtn.innerText = "Starting...";

    try {
        const response = await fetch(`${API_URL}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, text, wpm, cleanup })
        });

        const data = await response.json();

        if (data.status === "error") {
            showToast(data.message, "error");
            startBtn.disabled = false;
            startBtn.innerText = "Start Typing";
            return;
        }

        showToast("Started! Check your browser.", "success");
        pollInterval = setInterval(pollStatus, 1000);

        // Update UI state
        startBtn.classList.add("hidden");
        stopBtn.classList.remove("hidden");
        statusBadge.innerText = "Running";
        statusBadge.classList.add("bg-green-600", "animate-pulse");
        statusBadge.classList.remove("bg-gray-700");

    } catch (e) {
        console.error(e);
        showToast("Failed to start typing session", "error");
        startBtn.disabled = false;
        startBtn.innerText = "Start Typing";
    }
}

async function stopTyping() {
    try {
        await fetch(`${API_URL}/stop`, { method: "POST" });
        showToast("Stopping...", "info");
    } catch (e) {
        console.error(e);
    }
}

let pollInterval;

async function pollStatus() {
    try {
        const res = await fetch(`${API_URL}/status`);
        const data = await res.json();

        // Update Progress
        const progress = data.progress || 0;
        progressBar.style.width = `${progress}%`;
        progressText.innerText = `${progress}%`;
        statusMsg.innerText = data.status;

        // Check if finished
        if (!data.is_running) {
            clearInterval(pollInterval);
            resetUI();
            if (data.status === "Completed") {
                showToast("Typing Complete!", "success");
            } else if (data.status.startsWith("Error")) {
                showToast(data.status, "error");
            }
        }
    } catch (e) {
        console.error("Poll error", e);
    }
}

function resetUI() {
    startBtn.classList.remove("hidden");
    stopBtn.classList.add("hidden");
    startBtn.disabled = false;
    startBtn.innerText = "Start Typing";
    statusBadge.innerText = "Idle";
    statusBadge.classList.remove("bg-green-600", "animate-pulse");
    statusBadge.classList.add("bg-gray-700");
}
