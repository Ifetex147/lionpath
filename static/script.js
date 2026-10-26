let sessionId = null;
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");

// Speech synthesis (TTS)
let availableVoices = [];

function loadVoices() {
    availableVoices = window.speechSynthesis.getVoices();
}

if ("speechSynthesis" in window) {
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
}

function speakText(text) {
    if (!("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    const cleanText = text
        .replace(/\[\[PHOTO:.*?\]\]/g, "")
        .replace(/[-*#_~`]/g, "")
        .replace(/\b\d+\.\s+/g, "")
        .replace(/\s+/g, " ")
        .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05; 
    utterance.pitch = 1.0;

    if (availableVoices.length === 0) {
        availableVoices = window.speechSynthesis.getVoices();
    }

    const preferredVoice = availableVoices.find(
        (v) =>
            v.lang.startsWith("en") &&
            (v.name.includes("Natural") ||
                v.name.includes("Google") ||
                v.name.includes("Online") ||
                v.name.includes("Neural"))
    ) || availableVoices.find((v) => v.lang.startsWith("en"));

    if (preferredVoice) {
        utterance.voice = preferredVoice;
    }

    window.speechSynthesis.speak(utterance);
}

// Markdown parsing and photo rendering
function formatMarkdown(text) {
    if (!text) return "";

    // Escape HTML to prevent injection
    let safe = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

    // Inline Turn-by-Turn Waypoint/Destination Photos directly after each direction
    safe = safe.replace(/\[\[PHOTO:(.*?):(.*?):(.*?)\]\]/g, function(match, photo, name, type) {
        const isDest = (type === "dest");
        const badgeLabel = isDest ? "🎯 Destination Landmark" : "📍 Waypoint Landmark";
        const badgeClass = isDest ? "bg-success" : "bg-primary";
        return `
            <div class="step-photo-card p-2 bg-light rounded-3 border my-2 shadow-sm" style="max-width: 480px;">
                <div class="d-flex align-items-center justify-content-between mb-1">
                    <span class="badge ${badgeClass}">${badgeLabel}</span>
                    <small class="text-dark fw-bold">${name}</small>
                </div>
                <img src="/static/${photo}" class="img-fluid rounded border" style="max-height: 220px; width: 100%; object-fit: cover;" alt="${name}" onerror="if (this.closest('.step-photo-card')) this.closest('.step-photo-card').style.display='none';">
            </div>
        `;
    });

    // Bold (**text**)
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic (*text*)
    safe = safe.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Inline Code (`code`)
    safe = safe.replace(/`(.*?)`/g, "<code class='bg-light text-dark px-1 py-0.5 rounded'>$1</code>");

    return safe;
}

// Typing indicator
function showTypingIndicator() {
    removeTypingIndicator();

    const wrapper = document.createElement("div");
    wrapper.id = "typing-wrapper";
    wrapper.style.display = "flex";
    wrapper.style.marginBottom = "20px";
    wrapper.style.alignItems = "flex-end";
    wrapper.style.justifyContent = "flex-start";

    const avatar = document.createElement("div");
    avatar.textContent = "🦁";
    avatar.style.fontSize = "1.8rem";
    avatar.style.marginRight = "10px";
    avatar.style.marginBottom = "2px";
    wrapper.appendChild(avatar);

    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    wrapper.appendChild(indicator);

    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-wrapper");
    if (el) el.remove();
}

// Chat messaging UI
function addMessage(text, isUser, imageUrl = null, options = [], routeData = null) {
    const wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    wrapper.style.marginBottom = "20px";
    wrapper.style.alignItems = "flex-end";
    wrapper.style.justifyContent = isUser ? "flex-end" : "flex-start";

    if (!isUser) {
        const avatar = document.createElement("div");
        avatar.textContent = "🦁";
        avatar.style.fontSize = "1.8rem";
        avatar.style.marginRight = "10px";
        avatar.style.marginBottom = "2px";
        wrapper.appendChild(avatar);
    }

    const div = document.createElement("div");
    div.className = "message " + (isUser ? "user-msg" : "bot-msg");
    
    if (isUser) {
        div.textContent = text;
    } else {
        div.innerHTML = formatMarkdown(text);
    }

    // Standalone image fallback (if not already embedded in route directions)
    if (imageUrl) {
        // Fallback for standalone destination image
        const img = document.createElement("img");
        img.src = "/static/" + imageUrl;
        img.style.maxWidth = "100%";
        img.style.borderRadius = "8px";
        img.style.marginTop = "10px";
        img.style.display = "block";
        img.style.border = "1px solid #e2e8f0";
        div.appendChild(img);
    }

    // Attach quick-reply suggestion chips if available
    if (options && options.length > 0) {
        const chipsContainer = document.createElement("div");
        chipsContainer.className = "quick-replies-container";
        
        options.forEach(opt => {
            const chip = document.createElement("button");
            chip.className = "quick-chip";
            chip.textContent = opt;
            chip.onclick = function() {
                // Disable all chips in this container to prevent double submission
                chipsContainer.querySelectorAll(".quick-chip").forEach(b => b.disabled = true);
                sendMessage(opt);
            };
            chipsContainer.appendChild(chip);
        });

        div.appendChild(chipsContainer);
    }

    wrapper.appendChild(div);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(presetText = null) {
    const text = (presetText !== null ? presetText : input.value).trim();
    if (!text) return;

    addMessage(text, true);
    input.value = "";
    sendBtn.disabled = true;

    showTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });
        const data = await response.json();
        sessionId = data.session_id;

        removeTypingIndicator();
        addMessage(data.reply, false, data.image, data.options, data);

        const toggleElement = document.getElementById("audioToggle");
        if (toggleElement && toggleElement.checked) {
            speakText(data.reply);
        }

    } catch (err) {
        removeTypingIndicator();
        addMessage("Something went wrong. Please check your connection and try again.", false);
    }

    sendBtn.disabled = false;
    input.focus();
}

sendBtn.addEventListener("click", () => sendMessage());
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});

// Quick-reply chip listeners
document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', function() {
        const q = this.getAttribute('data-query') || this.textContent;
        sendMessage(q);
    });
});

// Speech recognition (STT)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition && micBtn) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-NG'; 
    recognition.interimResults = false;

    micBtn.addEventListener("click", () => {
        recognition.start();
        micBtn.textContent = "🔴"; 
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        input.value = transcript;
    };

    recognition.onend = () => {
        micBtn.textContent = "🎤"; 
        if (input.value.trim() !== "") {
            sendMessage(); 
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        micBtn.textContent = "🎤"; 
    };
} else if (micBtn) {
    micBtn.style.display = "none";
}

// --- INITIAL WELCOME GREETING WITH SUGGESTION CHIPS ---
window.addEventListener("DOMContentLoaded", () => {
    

    addMessage(
        "👋 **Welcome to LionPath!** I am your digital campus assistant for the Faculty of Physical Sciences, UNN.\n\n" +
        "Here are things you can ask me:\n" +
        "• 🗺️ **Campus Directions**: *'How do I get to SLT from CS?'* or *'Where is Carver Building?'*\n" +
        "• 🕒 **Lecture Schedules**: *'What time is COS 101?'* or *'Classes on Monday'*\n" +
        "• 📚 **Orientation & Clearance**: *'Clearance deadline'*, *'How do I pay fees?'*, *'Hostel room'*\n" +
        "• 🎓 **Grading**: *'How is CGPA calculated?'* or *'5-point scale'*\n\n" +
        "Click a quick option below or type your question:",
        false,
        null,
        ["Directions to SLT", "What time is COS 101?", "Clearance Deadline", "CGPA Calculation"]
    );
});
