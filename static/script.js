let sessionId = null;
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");

// --- CAMPUS MAP DATA & COORDINATES ---
const CAMPUS_NODES = {
    1:  { id: 1,  x: 170, y: 220, name: "Computer Science", fullName: "Computer Science Building", icon: "💻", color: "#2563eb", desc: "Three-storey brown block with computing labs." },
    11: { id: 11, x: 310, y: 220, name: "Faculty Quadrangle", fullName: "Faculty Quadrangle and Car Park", icon: "🚗", color: "#64748b", desc: "Open courtyard and parking area between CS and Physics." },
    7:  { id: 7,  x: 450, y: 220, name: "Faculty Junction", fullName: "Physical Sciences Junction", icon: "🚦", color: "#f59e0b", desc: "Central crossroad connecting CS, Physics, Math, and Library paths." },
    2:  { id: 2,  x: 450, y: 120, name: "Physics & Astronomy", fullName: "Physics and Astronomy Building", icon: "🔭", color: "#8b5cf6", desc: "White building with the iconic rooftop observatory dome." },
    3:  { id: 3,  x: 640, y: 120, name: "Maths & Statistics", fullName: "Mathematics and Statistics Building", icon: "📐", color: "#4f46e5", desc: "Two-storey block next to Physics with lecture halls." },
    6:  { id: 6,  x: 680, y: 220, name: "Science Library", fullName: "Faculty of Physical Sciences Library", icon: "📚", color: "#0d5c2e", desc: "Dedicated faculty study library with reference archives." },
    8:  { id: 8,  x: 450, y: 320, name: "Science Lecture Theatre", fullName: "Science Lecture Theatre (SLT)", icon: "🎭", color: "#db2777", desc: "Large tiered lecture hall for 100-level core lectures." },
    12: { id: 12, x: 290, y: 320, name: "Science Canteen", fullName: "Faculty Science Canteen", icon: "🍲", color: "#ea580c", desc: "Food canteen behind SLT serving local dishes and snacks." },
    4:  { id: 4,  x: 590, y: 320, name: "Chemistry Dept", fullName: "Chemistry Department Building", icon: "🧪", color: "#0891b2", desc: "Chemistry laboratories and lecture rooms opposite SLT." },
    5:  { id: 5,  x: 750, y: 320, name: "Geology Dept", fullName: "Geology Department Building", icon: "🪨", color: "#65a30d", desc: "Two-storey block with outdoor rock specimen displays." },
    9:  { id: 9,  x: 450, y: 410, name: "Carver Building", fullName: "Carver Building", icon: "🏛️", color: "#b45309", desc: "Administrative and lecture facility with photocopying shops." },
    10: { id: 10, x: 620, y: 410, name: "Abuja Building", fullName: "Abuja Building", icon: "🏢", color: "#0284c7", desc: "Multi-purpose lecture building opposite Carver Building." },
    13: { id: 13, x: 450, y: 520, name: "Student Union (SUB)", fullName: "Student Union Building", icon: "🦁", color: "#16a34a", desc: "Central student hub with stores, convenience kiosks, and parliament." },
    16: { id: 16, x: 250, y: 520, name: "Franco Refectory", fullName: "Franco Refectory", icon: "🍽️", color: "#dc2626", desc: "Main student dining refectory offering affordable meals." },
    14: { id: 14, x: 680, y: 520, name: "Main Library (NAL)", fullName: "Nnamdi Azikiwe Library", icon: "🏛️", color: "#4338ca", desc: "Flagship UNN university library with digital archives." },
    15: { id: 15, x: 680, y: 620, name: "Medical Centre", fullName: "University Medical Centre", icon: "🏥", color: "#e11d48", desc: "Campus health clinic providing 24/7 outpatient care." }
};

const CAMPUS_EDGES = [
    [1, 7], [1, 11],
    [7, 2], [7, 6], [7, 3],
    [3, 2],
    [7, 8],
    [8, 4], [4, 5],
    [8, 12],
    [7, 9],
    [9, 10],
    [9, 13],
    [13, 16],
    [13, 14],
    [14, 15]
];

// --- TEXT-TO-SPEECH (Voice Output) ---
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

// --- MARKDOWN FORMATTING ---
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

// --- TYPING INDICATOR ---
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

// --- UI AND MESSAGING ---
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

    // Attach "View Route on Map" button if route data is present
    if (routeData && routeData.route_nodes && routeData.route_nodes.length > 1) {
        const mapBtnDiv = document.createElement("div");
        mapBtnDiv.className = "mt-2 pt-1";
        
        const mapBtn = document.createElement("button");
        mapBtn.className = "btn btn-sm btn-success rounded-pill fw-semibold shadow-sm px-3 py-1 d-inline-flex align-items-center gap-1";
        mapBtn.innerHTML = '<span>🗺️</span> <span>View Route on Campus Map</span>';
        mapBtn.onclick = () => {
            highlightRouteOnMap(routeData);
        };
        mapBtnDiv.appendChild(mapBtn);
        div.appendChild(mapBtnDiv);
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

// --- GLOBAL CHIPS LISTENER ---
document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', function() {
        const q = this.getAttribute('data-query') || this.textContent;
        sendMessage(q);
    });
});

// --- SPEECH-TO-TEXT (Voice Input) ---
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

// =========================================================================
// INTERACTIVE SVG CAMPUS MAP ENGINE
// =========================================================================
function initCampusMap() {
    const edgesGroup = document.getElementById("mapEdgesGroup");
    const nodesGroup = document.getElementById("mapNodesGroup");
    if (!edgesGroup || !nodesGroup) return;

    edgesGroup.innerHTML = "";
    nodesGroup.innerHTML = "";

    // 1. Draw Static Walkways
    CAMPUS_EDGES.forEach(([uId, vId]) => {
        const u = CAMPUS_NODES[uId];
        const v = CAMPUS_NODES[vId];
        if (!u || !v) return;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", u.x);
        line.setAttribute("y1", u.y);
        line.setAttribute("x2", v.x);
        line.setAttribute("y2", v.y);
        line.setAttribute("class", "map-edge");
        edgesGroup.appendChild(line);
    });

    // 2. Draw Landmark Nodes
    Object.values(CAMPUS_NODES).forEach((node) => {
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "map-node-group");
        g.setAttribute("data-id", node.id);

        // Shadow ring
        const shadow = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        shadow.setAttribute("cx", node.x);
        shadow.setAttribute("cy", node.y);
        shadow.setAttribute("r", 18);
        shadow.setAttribute("fill", "#ffffff");
        shadow.setAttribute("stroke", "#e2e8f0");
        shadow.setAttribute("stroke-width", "2");

        // Main colored circle
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", node.x);
        circle.setAttribute("cy", node.y);
        circle.setAttribute("r", 15);
        circle.setAttribute("fill", node.color);
        circle.setAttribute("class", "node-circle");

        // Icon text
        const icon = document.createElementNS("http://www.w3.org/2000/svg", "text");
        icon.setAttribute("x", node.x);
        icon.setAttribute("y", node.y + 5);
        icon.setAttribute("text-anchor", "middle");
        icon.setAttribute("font-size", "13");
        icon.textContent = node.icon;

        // Label text below node
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", node.x);
        label.setAttribute("y", node.y + 32);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("font-size", "11");
        label.setAttribute("font-weight", "600");
        label.setAttribute("fill", "#1e293b");
        label.setAttribute("class", "node-label");
        label.textContent = node.name;

        g.appendChild(shadow);
        g.appendChild(circle);
        g.appendChild(icon);
        g.appendChild(label);

        // Click to view landmark card
        g.addEventListener("click", () => showLandmarkInfo(node));

        nodesGroup.appendChild(g);
    });
}

function showLandmarkInfo(node) {
    const card = document.getElementById("landmarkInfoCard");
    if (!card) return;

    document.getElementById("landmarkCardIcon").textContent = node.icon;
    document.getElementById("landmarkCardName").textContent = node.fullName;
    document.getElementById("landmarkCardCategory").textContent = node.cat || "Landmark";
    document.getElementById("landmarkCardDesc").textContent = node.desc || "Registered campus landmark.";

    const navBtn = document.getElementById("btnNavToHere");
    if (navBtn) {
        navBtn.onclick = () => {
            const modalEl = document.getElementById("campusMapModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            sendMessage(`Directions to ${node.fullName}`);
        };
    }

    card.style.display = "block";
}

function highlightRouteOnMap(routeData) {
    if (!routeData || !routeData.route_nodes || routeData.route_nodes.length === 0) return;

    // Show Bootstrap Modal
    const modalEl = document.getElementById("campusMapModal");
    if (modalEl && window.bootstrap) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }

    const activeGroup = document.getElementById("mapActiveRouteGroup");
    const pinsGroup = document.getElementById("mapPinsGroup");
    const banner = document.getElementById("mapRouteBanner");
    const title = document.getElementById("bannerRouteTitle");
    const stats = document.getElementById("bannerRouteStats");

    if (!activeGroup || !pinsGroup) return;

    activeGroup.innerHTML = "";
    pinsGroup.innerHTML = "";

    const nodes = routeData.route_nodes
        .map(id => CAMPUS_NODES[id])
        .filter(n => n !== undefined);

    if (nodes.length < 2) return;

    // Draw active animated path
    const pathD = nodes.map((n, i) => `${i === 0 ? "M" : "L"} ${n.x} ${n.y}`).join(" ");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathD);
    path.setAttribute("class", "route-active-line");
    activeGroup.appendChild(path);

    // Place START Pulse Pin
    const startNode = nodes[0];
    const startPulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    startPulse.setAttribute("cx", startNode.x);
    startPulse.setAttribute("cy", startNode.y);
    startPulse.setAttribute("class", "node-pulse-start");
    startPulse.setAttribute("fill", "rgba(16, 185, 129, 0.4)");
    pinsGroup.appendChild(startPulse);

    // Place DESTINATION Pulse Pin
    const endNode = nodes[nodes.length - 1];
    const endPulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    endPulse.setAttribute("cx", endNode.x);
    endPulse.setAttribute("cy", endNode.y);
    endPulse.setAttribute("class", "node-pulse-dest");
    endPulse.setAttribute("fill", "rgba(239, 68, 68, 0.45)");
    pinsGroup.appendChild(endPulse);

    // Update banner
    if (banner && title && stats) {
        banner.style.display = "flex";
        title.textContent = `Route: ${routeData.source_name || startNode.name} ➔ ${routeData.destination_name || endNode.name}`;
        stats.textContent = `Distance: ~${routeData.total_distance || 0} meters • Est. Walking Time: ~${routeData.est_mins || 1} min(s)`;
    }
}

function clearMapHighlight() {
    const activeGroup = document.getElementById("mapActiveRouteGroup");
    const pinsGroup = document.getElementById("mapPinsGroup");
    const banner = document.getElementById("mapRouteBanner");
    const card = document.getElementById("landmarkInfoCard");

    if (activeGroup) activeGroup.innerHTML = "";
    if (pinsGroup) pinsGroup.innerHTML = "";
    if (banner) banner.style.display = "none";
    if (card) card.style.display = "none";
}

// --- INITIAL WELCOME GREETING WITH SUGGESTION CHIPS ---
window.addEventListener("DOMContentLoaded", () => {
    initCampusMap();

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
        ["🗺️ Directions to SLT", "🕒 What time is COS 101?", "📚 Clearance Deadline", "🎓 CGPA Calculation"]
    );
});
