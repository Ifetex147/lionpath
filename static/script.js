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

    // Attach "View Route on Campus Map" button if route data is present
    if (routeData && routeData.route_nodes && routeData.route_nodes.length > 1) {
        const mapBtnDiv = document.createElement("div");
        mapBtnDiv.className = "mt-3 pt-1";
        
        const mapBtn = document.createElement("button");
        mapBtn.className = "btn btn-sm btn-success rounded-pill fw-semibold shadow-sm px-3 py-2 d-inline-flex align-items-center gap-2";
        mapBtn.innerHTML = '<span>🗺️</span> <span>View Animated Route on Campus Map</span>';
        mapBtn.onclick = () => {
            openCampusMap(routeData);
        };
        mapBtnDiv.appendChild(mapBtn);
        div.appendChild(mapBtnDiv);
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


// ==========================================
// 🗺️ 2D INTERACTIVE CAMPUS MAP (ALL 27 NODES)
// ==========================================

const CAMPUS_NODES = {
    // 1. Physical Sciences Cluster (Upper Center)
    1:  { id: 1,  x: 420, y: 330, name: "Carver Building", fullName: "Carver Building (Computer Science)", category: "Academic Building", icon: "🏛️", color: "#0d5c2e", photo: "carver_building.jpeg", desc: "Three-storey building housing the Department of Computer Science and Faculty administrative offices." },
    4:  { id: 4,  x: 640, y: 330, name: "Abuja Building", fullName: "Abuja Building (Prof. Ezeilo Building)", category: "Academic Building", icon: "🏢", color: "#0284c7", photo: "abuja_building.jpeg", desc: "Multi-storey building facing Carver, housing Mathematics and Statistics lecture theatres." },
    6:  { id: 6,  x: 320, y: 330, name: "New CS (NCSB)", fullName: "New Computer Science Building (NCSB)", category: "Academic Building", icon: "💻", color: "#2563eb", photo: "computer_science.jpeg", desc: "Modern lecture hall and computer lab facility for Computer Science students." },
    10: { id: 10, x: 530, y: 250, name: "FPSLT (SLT)", fullName: "Faculty of Physical Sciences Lecture Theatre (FPSLT)", category: "Lecture Theatre", icon: "🎭", color: "#db2777", photo: "fpslt.jpeg", desc: "Main faculty lecture theatre hosting 100-level core lectures and official freshmen matriculation." },
    24: { id: 24, x: 420, y: 250, name: "Science Canteen", fullName: "Faculty Science Canteen", category: "Dining", icon: "🍲", color: "#dc2626", photo: "canteen.jpeg", desc: "Faculty food canteen situated right behind SLT/FPSLT serving meals and refreshments." },
    5:  { id: 5,  x: 320, y: 230, name: "SLT Dept", fullName: "Science Laboratory Technology (SLT) Department", category: "Department", icon: "🔬", color: "#0891b2", photo: "slt_department.jpeg", desc: "Department of Science Laboratory Technology with specialised practical laboratories." },
    23: { id: 23, x: 440, y: 160, name: "Faculty Library", fullName: "Faculty of Physical Sciences Library", category: "Library", icon: "📖", color: "#0d5c2e", photo: "faculty_library.jpeg", desc: "Dedicated faculty science library holding subject archives and research reading spaces." },
    25: { id: 25, x: 670, y: 240, name: "Maths & Stats", fullName: "Mathematics and Statistics Building", category: "Department", icon: "📐", color: "#4338ca", photo: "mathematics.jpeg", desc: "Departmental lecture rooms, computer statistics laboratories, and lecturer offices." },
    26: { id: 26, x: 540, y: 140, name: "Physics & Astro", fullName: "Physics and Astronomy Building", category: "Department", icon: "🔭", color: "#8b5cf6", photo: "physics.jpeg", desc: "Iconic landmark with astronomical rooftop telescope dome and experimental laboratories." },
    27: { id: 27, x: 710, y: 140, name: "Chemistry Dept", fullName: "Chemistry Department Building", category: "Department", icon: "🧪", color: "#0891b2", photo: "chemistry.jpeg", desc: "Chemistry laboratories for organic, inorganic, and physical practical science sessions." },
    11: { id: 11, x: 810, y: 220, name: "Geology Dept", fullName: "Geology Department Building", category: "Department", icon: "🪨", color: "#65a30d", photo: "geology_department.jpeg", desc: "Geology department with museum collections and outdoor mineral/rock specimen displays." },

    // 2. Central Administration & Heritage Avenue (Middle-Lower Center)
    8:  { id: 8,  x: 530, y: 470, name: "VC's Office", fullName: "Vice-Chancellor's Office (VC's Office)", category: "Administrative", icon: "🏛️", color: "#4338ca", photo: "vc_building_front.jpeg", desc: "White central administration building facing NAL housing top university principal officers." },
    2:  { id: 2,  x: 690, y: 470, name: "NAL Library", fullName: "Nnamdi Azikiwe Library (NAL)", category: "Library", icon: "📚", color: "#1e40af", photo: "nnamdi_azikiwke_library.jpeg", desc: "Iconic flagship central university library of UNN with extensive digital archives." },
    3:  { id: 3,  x: 390, y: 470, name: "Student Affairs", fullName: "Student Affairs Building", category: "Administrative", icon: "🦁", color: "#065f46", photo: "student_affairs.jpeg", desc: "Central student affairs division; walkway leads uphill to Ekpo Ref." },
    22: { id: 22, x: 530, y: 560, name: "ICT Centre", fullName: "University ICT Centre", category: "Technology", icon: "🖥️", color: "#2563eb", photo: "ict.jpeg", desc: "Campus computing center managing UNN student portal, Lionet Wi-Fi, and CBT exams." },
    12: { id: 12, x: 690, y: 560, name: "Bookshop", fullName: "University Bookshop", category: "Campus Facility", icon: "📖", color: "#ca8a04", photo: "bookshop.jpeg", desc: "Official university academic bookstore stocking textbooks, stationery, and publications." },
    21: { id: 21, x: 390, y: 560, name: "Admission Block", fullName: "Admission Office (Admission Block)", category: "Administrative", icon: "📋", color: "#4f46e5", photo: "admission_block.jpeg", desc: "Administrative office handling undergraduate admissions, JAMB regularization, and files." },
    14: { id: 14, x: 310, y: 630, name: "GS Building", fullName: "General Studies Building (GS Building)", category: "Academic Building", icon: "🏛️", color: "#16a34a", photo: "gs_building.jpeg", desc: "Large green administrative building for General Studies courses (GSP 101, GSP 111)." },
    13: { id: 13, x: 825, y: 510, name: "Medical Centre", fullName: "University Medical Centre", category: "Health Facility", icon: "🏥", color: "#e11d48", photo: "medical_center.jpeg", desc: "Comprehensive campus health centre providing 24/7 medical treatment and registration." },

    // 3. Student Living & Hostels (West / Left Corridor, leading up from 2nd Gate)
    7:  { id: 7,  x: 150, y: 370, name: "Bello Hall", fullName: "Bello Hall (Hostel)", category: "Student Hostel", icon: "🏠", color: "#d97706", photo: "bello_hostel.jpeg", desc: "Historic male student residence hall situated in the western residential quadrangle." },
    20: { id: 20, x: 150, y: 450, name: "Eyo-Ita Hall", fullName: "Eyo-Ita Hall (Hostel)", category: "Student Hostel", icon: "🏠", color: "#b45309", photo: "eyo_ita_hostel.jpeg", desc: "Undergraduate hostel facility opposite Bello Hall in the student living corridor." },
    18: { id: 18, x: 150, y: 530, name: "Aja-Nwachukwu", fullName: "Aja-Nwachukwu Hall (Hostel)", category: "Student Hostel", icon: "🏠", color: "#ea580c", photo: "aja_nwachukwu_hostel.jpeg", desc: "Undergraduate student hostel in the western campus residential sector." },
    19: { id: 19, x: 150, y: 610, name: "Akintola Hall", fullName: "Akintola Hall (Hostel)", category: "Student Hostel", icon: "🏠", color: "#d97706", photo: "akintola_hostel.jpeg", desc: "Multi-storey student accommodation located near Aja-Nwachukwu Hall." },

    // 4. Perimeter Campus Gates
    15: { id: 15, x: 780, y: 730, name: "UNN 1st Gate", fullName: "UNN 1st Gate (Main Gate)", category: "Main Entrance", icon: "🚪", color: "#047857", photo: "main_gate.jpeg", desc: "The grand ceremonial main entrance gate to the University of Nigeria from Nsukka town." },
    16: { id: 16, x: 150, y: 730, name: "UNN 2nd Gate", fullName: "UNN 2nd Gate (Abuja / Franco Gate)", category: "Secondary Gate", icon: "🚪", color: "#0284c7", photo: "abuja_gate.jpeg", desc: "Secondary campus gate near Franco refectory and hostels connecting commuters from Green House area." },
    17: { id: 17, x: 150, y: 140,  name: "Odenigwe Gate", fullName: "Odenigwe Campus Gate", category: "Perimeter Gate", icon: "🚪", color: "#7c3aed", photo: "odenigwe_gate.jpeg", desc: "Northern campus gate serving as primary transit corridor for Odenigwe lodge residents." },
    9:  { id: 9,  x: 920, y: 420, name: "Odim Gate", fullName: "Odim Campus Gate", category: "Perimeter Gate", icon: "🚪", color: "#7c3aed", photo: "odim_gate.jpeg", desc: "Eastern campus gate connecting UNN to Odim off-campus student residential lodges." }
};

const CAMPUS_EDGES = [
    // 1. Perimeter Gates to Campus Arteries
    [15, 2], [15, 12], [15, 13], [15, 14],
    [16, 4], [16, 1], [16, 19], [16, 14],
    [17, 7], [17, 5], [17, 6],
    [9, 11], [9, 13], [9, 4],

    // 2. Student Living Corridor (Western axis)
    [19, 18], [18, 20], [20, 7], [7, 3], [18, 3], [18, 1],

    // 3. Central Administration & Heritage Avenue
    [14, 21], [21, 22], [22, 12], [12, 13],
    [14, 3], [3, 8], [8, 2], [2, 12], [8, 22], [2, 13],

    // 4. Link between Central Admin & Physical Sciences
    [3, 1], [8, 1], [2, 1], [2, 4], [22, 4],

    // 5. Faculty of Physical Sciences Quadrangle
    [1, 6], [1, 4], [1, 24], [1, 10], [1, 23], [1, 26],
    [6, 5], [5, 24], [24, 10], [10, 4],
    [4, 25], [25, 11], [26, 27], [27, 11], [23, 26], [5, 10]
];

let mapInitialized = false;
let mapModalInstance = null;
let currentViewBox = { x: 0, y: 0, w: 1000, h: 800 };

function initCampusMap() {
    if (mapInitialized) return;

    const svg = document.getElementById("campusSvgMap");
    const edgesGroup = document.getElementById("mapEdgesGroup");
    const nodesGroup = document.getElementById("mapNodesGroup");

    if (!svg || !edgesGroup || !nodesGroup) return;

    // 1. Render all 55 walkway connections
    edgesGroup.innerHTML = "";
    CAMPUS_EDGES.forEach(([sId, dId]) => {
        const sNode = CAMPUS_NODES[sId];
        const dNode = CAMPUS_NODES[dId];
        if (!sNode || !dNode) return;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", sNode.x);
        line.setAttribute("y1", sNode.y);
        line.setAttribute("x2", dNode.x);
        line.setAttribute("y2", dNode.y);
        line.setAttribute("class", "map-edge");
        edgesGroup.appendChild(line);
    });

    // 2. Render all 27 Landmark Nodes as clean white pill cards
    nodesGroup.innerHTML = "";
    Object.values(CAMPUS_NODES).forEach(node => {
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "map-node-group");
        g.setAttribute("id", `node-group-${node.id}`);
        g.setAttribute("transform", `translate(${node.x}, ${node.y})`);
        g.onclick = () => selectLandmarkNode(node.id);

        // White card background with subtle accent border
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("class", "node-card-bg");
        rect.setAttribute("x", "-48");
        rect.setAttribute("y", "-16");
        rect.setAttribute("width", "96");
        rect.setAttribute("height", "32");
        rect.setAttribute("rx", "16");
        rect.setAttribute("fill", "#ffffff");
        rect.setAttribute("stroke", node.color);
        rect.setAttribute("stroke-width", "1.8");
        rect.setAttribute("filter", "url(#nodeShadow)");

        // Icon circle
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", "-30");
        circle.setAttribute("cy", "0");
        circle.setAttribute("r", "11");
        circle.setAttribute("fill", node.color);
        circle.setAttribute("fill-opacity", "0.15");

        // Icon Emoji
        const icon = document.createElementNS("http://www.w3.org/2000/svg", "text");
        icon.setAttribute("x", "-30");
        icon.setAttribute("y", "4");
        icon.setAttribute("font-size", "11");
        icon.setAttribute("text-anchor", "middle");
        icon.textContent = node.icon;

        // Label text
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("class", "node-label");
        label.setAttribute("x", "10");
        label.setAttribute("y", "3.5");
        label.setAttribute("font-size", "9.5");
        label.setAttribute("font-weight", "700");
        label.setAttribute("fill", "#0f172a");
        label.setAttribute("text-anchor", "middle");
        label.textContent = node.name;

        g.appendChild(rect);
        g.appendChild(circle);
        g.appendChild(icon);
        g.appendChild(label);
        nodesGroup.appendChild(g);
    });

    mapInitialized = true;
}

function openCampusMap(routeData = null) {
    initCampusMap();

    const modalEl = document.getElementById("campusMapModal");
    if (!modalEl) return;

    if (!mapModalInstance) {
        mapModalInstance = new bootstrap.Modal(modalEl);
    }
    mapModalInstance.show();

    if (routeData && routeData.route_nodes && routeData.route_nodes.length > 1) {
        highlightRouteOnMap(routeData);
    } else {
        clearMapHighlight();
    }
}

function highlightRouteOnMap(routeData) {
    const activeRouteGroup = document.getElementById("mapActiveRouteGroup");
    const pinsGroup = document.getElementById("mapPinsGroup");
    const banner = document.getElementById("mapRouteBanner");
    const titleEl = document.getElementById("bannerRouteTitle");
    const statsEl = document.getElementById("bannerRouteStats");

    if (!activeRouteGroup || !pinsGroup) return;

    clearMapHighlight();

    // 1. Show Route Alert Banner
    if (banner && titleEl && statsEl) {
        titleEl.textContent = `Route: ${routeData.source_name || 'Start'} ➔ ${routeData.destination_name || 'Destination'}`;
        statsEl.textContent = `Distance: ~${routeData.total_distance || 0} meters • Est. Walk Time: ~${routeData.est_mins || 1} min${(routeData.est_mins || 1) > 1 ? 's' : ''}`;
        banner.style.display = "flex";
    }

    const nodeIds = routeData.route_nodes;

    // 2. Draw glowing animated emerald lines along traversed edges
    for (let i = 0; i < nodeIds.length - 1; i++) {
        const u = CAMPUS_NODES[nodeIds[i]];
        const v = CAMPUS_NODES[nodeIds[i + 1]];
        if (!u || !v) continue;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", u.x);
        line.setAttribute("y1", u.y);
        line.setAttribute("x2", v.x);
        line.setAttribute("y2", v.y);
        line.setAttribute("class", "route-active-line");
        activeRouteGroup.appendChild(line);
    }

    // 3. Highlight Start Node with pulsing green halo & START badge
    const startNode = CAMPUS_NODES[nodeIds[0]];
    if (startNode) {
        const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        pulse.setAttribute("cx", startNode.x);
        pulse.setAttribute("cy", startNode.y);
        pulse.setAttribute("r", "24");
        pulse.setAttribute("fill", "none");
        pulse.setAttribute("stroke", "#10b981");
        pulse.setAttribute("stroke-width", "3");
        pulse.setAttribute("class", "node-pulse-start");
        pinsGroup.appendChild(pulse);

        const startBadge = document.createElementNS("http://www.w3.org/2000/svg", "g");
        startBadge.setAttribute("transform", `translate(${startNode.x}, ${startNode.y - 24})`);
        startBadge.innerHTML = `
            <rect x="-30" y="-13" width="60" height="17" rx="8" fill="#10b981" filter="url(#nodeShadow)"/>
            <text x="0" y="-1" fill="#ffffff" font-size="8.5" font-weight="800" text-anchor="middle">🟢 START</text>
        `;
        pinsGroup.appendChild(startBadge);

        const g = document.getElementById(`node-group-${startNode.id}`);
        if (g) {
            const rect = g.querySelector(".node-card-bg");
            if (rect) {
                rect.setAttribute("fill", "#ecfdf5");
                rect.setAttribute("stroke", "#10b981");
                rect.setAttribute("stroke-width", "2.5");
            }
        }
    }

    // 4. Highlight Destination Node with pulsing red halo & DESTINATION badge
    const destNode = CAMPUS_NODES[nodeIds[nodeIds.length - 1]];
    if (destNode) {
        const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        pulse.setAttribute("cx", destNode.x);
        pulse.setAttribute("cy", destNode.y);
        pulse.setAttribute("r", "26");
        pulse.setAttribute("fill", "none");
        pulse.setAttribute("stroke", "#ef4444");
        pulse.setAttribute("stroke-width", "3");
        pulse.setAttribute("class", "node-pulse-dest");
        pinsGroup.appendChild(pulse);

        const destBadge = document.createElementNS("http://www.w3.org/2000/svg", "g");
        destBadge.setAttribute("transform", `translate(${destNode.x}, ${destNode.y - 24})`);
        destBadge.innerHTML = `
            <rect x="-44" y="-13" width="88" height="17" rx="8" fill="#dc2626" filter="url(#nodeShadow)"/>
            <text x="0" y="-1" fill="#ffffff" font-size="8.5" font-weight="800" text-anchor="middle">🏁 DESTINATION</text>
        `;
        pinsGroup.appendChild(destBadge);

        const g = document.getElementById(`node-group-${destNode.id}`);
        if (g) {
            const rect = g.querySelector(".node-card-bg");
            if (rect) {
                rect.setAttribute("fill", "#fee2e2");
                rect.setAttribute("stroke", "#dc2626");
                rect.setAttribute("stroke-width", "2.5");
            }
        }
    }

    // 5. Highlight intermediate nodes along path
    for (let i = 1; i < nodeIds.length - 1; i++) {
        const interNode = CAMPUS_NODES[nodeIds[i]];
        if (!interNode) continue;
        const g = document.getElementById(`node-group-${interNode.id}`);
        if (g) {
            const rect = g.querySelector(".node-card-bg");
            if (rect) {
                rect.setAttribute("fill", "#f0fdf4");
                rect.setAttribute("stroke", "#059669");
                rect.setAttribute("stroke-width", "2.2");
            }
        }
    }
}

function clearMapHighlight() {
    const activeRouteGroup = document.getElementById("mapActiveRouteGroup");
    const pinsGroup = document.getElementById("mapPinsGroup");
    const banner = document.getElementById("mapRouteBanner");

    if (activeRouteGroup) activeRouteGroup.innerHTML = "";
    if (pinsGroup) pinsGroup.innerHTML = "";
    if (banner) banner.style.display = "none";

    // Reset all node cards to initial clean styling
    Object.values(CAMPUS_NODES).forEach(node => {
        const g = document.getElementById(`node-group-${node.id}`);
        if (g) {
            const rect = g.querySelector(".node-card-bg");
            if (rect) {
                rect.setAttribute("fill", "#ffffff");
                rect.setAttribute("stroke", node.color);
                rect.setAttribute("stroke-width", "1.8");
            }
        }
    });
}

function selectLandmarkNode(nodeId) {
    const node = CAMPUS_NODES[nodeId];
    if (!node) return;

    const card = document.getElementById("landmarkInfoCard");
    const photo = document.getElementById("landmarkCardPhoto");
    const nameEl = document.getElementById("landmarkCardName");
    const catEl = document.getElementById("landmarkCardCategory");
    const descEl = document.getElementById("landmarkCardDesc");
    const btnNav = document.getElementById("btnNavToHere");

    if (!card || !nameEl || !descEl || !btnNav) return;

    if (photo) photo.src = `/static/images/${node.photo}`;
    nameEl.textContent = node.fullName;
    if (catEl) catEl.textContent = node.category;
    descEl.textContent = node.desc;

    btnNav.onclick = () => {
        if (mapModalInstance) mapModalInstance.hide();
        sendMessage(`Directions to ${node.fullName}`);
    };

    card.style.display = "block";
}

function zoomMap(factor) {
    const svg = document.getElementById("campusSvgMap");
    if (!svg) return;

    const newW = currentViewBox.w / factor;
    const newH = currentViewBox.h / factor;
    const dx = (currentViewBox.w - newW) / 2;
    const dy = (currentViewBox.h - newH) / 2;

    currentViewBox.x += dx;
    currentViewBox.y += dy;
    currentViewBox.w = newW;
    currentViewBox.h = newH;

    svg.setAttribute("viewBox", `${currentViewBox.x} ${currentViewBox.y} ${currentViewBox.w} ${currentViewBox.h}`);
}

function resetMapZoom() {
    const svg = document.getElementById("campusSvgMap");
    if (!svg) return;

    currentViewBox = { x: 0, y: 0, w: 1000, h: 800 };
    svg.setAttribute("viewBox", "0 0 1000 800");
}
