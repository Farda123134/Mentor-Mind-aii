HTML_CONTENT = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>MENTOR MIND AI</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Segoe UI,sans-serif;background:#0f0f1a;color:#e8e8f0;height:100vh;overflow:hidden}

/* AUTH */
.auth-page{display:flex;align-items:center;justify-content:center;height:100vh;background:linear-gradient(135deg,#0f0f1a,#1a1a2e)}
.auth-box{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:16px;padding:40px;width:100%;max-width:420px}
.auth-logo{text-align:center;margin-bottom:28px}
.auth-logo .icon{width:56px;height:56px;background:linear-gradient(135deg,#6c63ff,#a78bfa);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 12px}
.auth-logo h1{font-size:22px;font-weight:700;color:#fff}
.auth-logo p{font-size:13px;color:#8888aa;margin-top:4px}
.auth-tabs{display:flex;background:#0f0f1a;border-radius:10px;padding:4px;margin-bottom:28px}
.auth-tab{flex:1;padding:8px;text-align:center;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500;color:#8888aa}
.auth-tab.active{background:#6c63ff;color:#fff}
.form-group{margin-bottom:18px}
.form-group label{display:block;font-size:12px;color:#8888aa;margin-bottom:6px;font-weight:500}
.form-group input{width:100%;background:#0f0f1a;border:1px solid #2a2a4a;border-radius:10px;padding:12px 14px;font-size:14px;color:#e8e8f0;outline:none}
.form-group input:focus{border-color:#6c63ff}
.form-group input::placeholder{color:#44446a}
.auth-btn{width:100%;background:linear-gradient(135deg,#6c63ff,#a78bfa);color:#fff;border:none;border-radius:10px;padding:13px;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
.auth-btn:disabled{opacity:.5;cursor:not-allowed}
.auth-error{background:#2d0a0a;border:1px solid #7f1d1d;color:#f87171;border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:16px;display:none}
.auth-success{background:#052e16;border:1px solid #166534;color:#4ade80;border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:16px;display:none}

/* APP LAYOUT */
.app{display:none;height:100vh}
.app.show{display:flex}

/* SIDEBAR */
.sidebar{width:260px;background:#13132a;border-right:1px solid #2a2a4a;display:flex;flex-direction:column;flex-shrink:0;transition:margin-left .2s}
.sidebar.collapsed{margin-left:-260px}
.sidebar-header{padding:14px;border-bottom:1px solid #2a2a4a}
.new-chat-btn{width:100%;background:#1e1b4b;color:#a78bfa;border:1px solid #4c1d95;border-radius:10px;padding:10px;font-size:13px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px}
.new-chat-btn:hover{background:#2a2566}
.history-label{font-size:11px;color:#666;padding:12px 14px 6px;text-transform:uppercase;letter-spacing:.05em}
.history-list{flex:1;overflow-y:auto;padding:0 8px}
.history-list::-webkit-scrollbar{width:3px}
.history-list::-webkit-scrollbar-thumb{background:#3a3a5c;border-radius:3px}
.history-item{padding:10px 10px;border-radius:8px;cursor:pointer;margin-bottom:2px;display:flex;align-items:center;gap:8px;position:relative}
.history-item:hover{background:#1e1e38}
.history-item.active{background:#272350}
.history-item .h-icon{font-size:13px;flex-shrink:0;opacity:.6}
.history-item .h-info{flex:1;min-width:0}
.history-item .h-title{font-size:12.5px;color:#d0d0e0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.history-item .h-date{font-size:10px;color:#666;margin-top:2px}
.history-item .h-actions{display:none;gap:4px}
.history-item:hover .h-actions{display:flex}
.h-action-btn{background:none;border:none;color:#888;cursor:pointer;font-size:12px;padding:3px 5px;border-radius:4px}
.h-action-btn:hover{background:#2a2a4a;color:#fff}
.sidebar-footer{padding:12px 14px;border-top:1px solid #2a2a4a}
.sidebar-user{font-size:11px;color:#8888aa;margin-bottom:8px;word-break:break-all}
.logout-btn{width:100%;background:#2d0a0a;color:#f87171;border:1px solid #7f1d1d;border-radius:8px;padding:7px;font-size:12px;cursor:pointer}

/* MAIN CHAT AREA */
.main-area{flex:1;display:flex;flex-direction:column;min-width:0}
header{background:#1a1a2e;border-bottom:1px solid #2a2a4a;padding:10px 20px;display:flex;align-items:center;gap:10px;flex-shrink:0}
.toggle-sidebar{background:none;border:none;color:#8888aa;cursor:pointer;font-size:18px;padding:4px 8px;border-radius:6px}
.toggle-sidebar:hover{background:#2a2a4a}
.logo{width:32px;height:32px;background:linear-gradient(135deg,#6c63ff,#a78bfa);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}
header h1{font-size:15px;font-weight:600;color:#fff;margin:0}
.sub{font-size:11px;color:#8888aa}
.badge{margin-left:auto;background:#0d2b1d;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #166534}
.pills{background:#13132a;border-bottom:1px solid #2a2a4a;padding:8px 20px;display:flex;gap:7px;flex-wrap:wrap;flex-shrink:0;align-items:center}
.pill{font-size:11px;padding:3px 12px;border-radius:20px;border:1px solid;cursor:pointer;background:#1e1b4b;color:#a78bfa;border-color:#4c1d95}
.pill.g{background:#052e16;color:#4ade80;border-color:#166534}
.pill.b{background:#0c1a3a;color:#60a5fa;border-color:#1e3a5f}
.pill.a{background:#2d1a00;color:#fbbf24;border-color:#78350f}
.pill.r{background:#2d0a0a;color:#f87171;border-color:#7f1d1d}
.pill.w{background:#1a1a2e;color:#aaa;border-color:#333}
.chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:14px}
.chat::-webkit-scrollbar{width:3px}
.chat::-webkit-scrollbar-thumb{background:#3a3a5c;border-radius:3px}
.row{display:flex;gap:9px;max-width:90%}
.row.me{align-self:flex-end;flex-direction:row-reverse}
.av{width:30px;height:30px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;background:linear-gradient(135deg,#6c63ff,#a78bfa);color:#fff}
.av.me{background:#2a2a4a;color:#a78bfa}
.bub{padding:10px 14px;border-radius:3px 14px 14px 14px;font-size:13px;line-height:1.7;max-width:100%;word-break:break-word;background:#1e1e38;border:1px solid #2a2a4a;color:#e8e8f0;white-space:pre-wrap}
.bub.me{background:#4c3fa0;color:#fff;border-radius:14px 3px 14px 14px;border:none}
.atag{font-size:10px;color:#6c63ff;margin-bottom:5px;font-weight:600}
.timer{font-size:10px;color:#444;margin-top:4px}
.dots{display:flex;gap:4px;align-items:center;padding:4px 0}
.dot{width:6px;height:6px;background:#6c63ff;border-radius:50%;animation:jmp 1.2s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes jmp{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-7px)}}
.tinfo{font-size:11px;color:#8888aa;margin-top:5px}
.pbar{height:2px;background:#2a2a4a;margin-top:7px;border-radius:1px;overflow:hidden}
.pfill{height:100%;background:linear-gradient(90deg,#6c63ff,#a78bfa);animation:ld 2s ease-in-out infinite}
@keyframes ld{0%{width:5%}50%{width:75%}100%{width:92%}}
.bottom{background:#1a1a2e;border-top:1px solid #2a2a4a;padding:14px 20px;display:flex;gap:9px;flex-shrink:0}
textarea{flex:1;background:#0f0f1a;border:1px solid #2a2a4a;border-radius:11px;padding:11px 14px;font-size:13px;color:#e8e8f0;outline:none;resize:none;font-family:inherit}
textarea:focus{border-color:#6c63ff}
textarea::placeholder{color:#44446a}
button.send{background:#6c63ff;color:#fff;border:none;border-radius:11px;padding:11px 20px;font-size:13px;font-weight:600;cursor:pointer}
button.send:disabled{background:#2a2a4a;color:#555;cursor:not-allowed}
.welcome{text-align:center;padding:30px 16px}
.welcome h2{font-size:20px;font-weight:600;margin-bottom:8px;background:linear-gradient(135deg,#6c63ff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{font-size:12px;color:#6666aa;margin-bottom:18px}
.sugs{display:flex;flex-wrap:wrap;justify-content:center;gap:7px}
.sug{background:#1e1e38;border:1px solid #2a2a4a;border-radius:18px;padding:6px 14px;font-size:12px;cursor:pointer;color:#a0a0cc}
.sug:hover{border-color:#6c63ff;color:#a78bfa}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #ffffff44;border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;margin-right:6px;vertical-align:-2px}
@keyframes spin{to{transform:rotate(360deg)}}

/* RENAME INPUT */
.rename-input{width:100%;background:#0f0f1a;border:1px solid #6c63ff;border-radius:6px;padding:4px 6px;font-size:12px;color:#fff;outline:none}
</style>
</head>
<body>

<div class="auth-page" id="authPage">
  <div class="auth-box">
    <div class="auth-logo">
      <div class="icon">&#127891;</div>
      <h1>MENTOR MIND AI</h1>
      <p>Your Personal AI Study Tutor</p>
    </div>
    <div class="auth-tabs">
      <div class="auth-tab active" onclick="showTab('login')">Login</div>
      <div class="auth-tab" onclick="showTab('signup')">Sign Up</div>
    </div>
    <div id="authError" class="auth-error"></div>
    <div id="authSuccess" class="auth-success"></div>
    <div id="loginForm">
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" id="loginEmail" placeholder="your@email.com" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" id="loginPassword" placeholder="Enter password" onkeydown="if(event.key==='Enter') doLogin()" />
      </div>
      <button class="auth-btn" id="loginBtn" onclick="doLogin()">Login</button>
    </div>
    <div id="signupForm" style="display:none">
      <div class="form-group">
        <label>Full Name</label>
        <input type="text" id="signupName" placeholder="Ali Ahmed" />
      </div>
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" id="signupEmail" placeholder="your@email.com" />
      </div>
      <div class="form-group">
        <label>Password (min 6 characters)</label>
        <input type="password" id="signupPassword" placeholder="Create password" onkeydown="if(event.key==='Enter') doSignup()" />
      </div>
      <button class="auth-btn" id="signupBtn" onclick="doSignup()">Create Account</button>
    </div>
  </div>
</div>

<div class="app" id="app">
  <!-- SIDEBAR -->
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
    </div>
    <div class="history-label">Chat History</div>
    <div class="history-list" id="historyList"></div>
    <div class="sidebar-footer">
      <div class="sidebar-user" id="userEmailDisplay"></div>
      <button class="logout-btn" onclick="doLogout()">Logout</button>
    </div>
  </div>

  <!-- MAIN -->
  <div class="main-area">
    <header>
      <button class="toggle-sidebar" onclick="toggleSidebar()">&#9776;</button>
      <div class="logo">&#127891;</div>
      <div><h1>MENTOR MIND AI</h1><div class="sub">Multi-Agent Learning System</div></div>
      <div class="badge">&#9679; 7 Agents Online</div>
    </header>
    <div class="pills">
      <span class="pill" onclick="go('Teach me AI Agents')">&#127891; Teacher</span>
      <span class="pill g" onclick="go('Create a 5 day Python plan')">&#128197; Planner</span>
      <span class="pill b" onclick="go('Show my progress')">&#129504; Memory</span>
      <span class="pill a" onclick="go('Quiz me on machine learning')">&#129514; Tester</span>
      <span class="pill r" onclick="go('Give me daily reminder')">&#9200; Scheduler</span>
      <span class="pill w" onclick="document.getElementById('fileInput').click()">&#128194; Upload</span>
      <input type="file" id="fileInput" accept=".pdf,.docx,.txt,.md" style="display:none" onchange="uploadFile()" />
      <span id="uploadStatus" style="font-size:11px;color:#8888aa"></span>
    </div>
    <div class="chat" id="chat">
      <div class="welcome" id="welcome">
        <h2>Welcome to MENTOR MIND AI</h2>
        <p>Start a new conversation or pick one from history</p>
        <div class="sugs">
          <div class="sug" onclick="go('Teach me AI Agents in 5 days')">Teach me AI in 5 days</div>
          <div class="sug" onclick="go('Explain neural networks')">Explain neural networks</div>
          <div class="sug" onclick="go('Quiz me on Python')">Quiz me on Python</div>
          <div class="sug" onclick="go('Create a 5 day data science plan')">5-day data science plan</div>
          <div class="sug" onclick="go('What is machine learning?')">What is ML?</div>
        </div>
      </div>
    </div>
    <div class="bottom">
      <textarea id="inp" rows="1" placeholder="Ask anything..."></textarea>
      <button class="send" id="sendBtn">Send</button>
    </div>
  </div>
</div>

<script>
var STATE = {
  accessToken: localStorage.getItem("mm_access_token") || "",
  sessionId: localStorage.getItem("mm_session_id") || "",
  userEmail: localStorage.getItem("mm_user_email") || "",
  currentChatId: "",
  t0: 0
};

window.addEventListener("DOMContentLoaded", function() {
  if (STATE.accessToken && STATE.sessionId) {
    showApp();
    loadChatList();
  } else {
    showAuth();
  }
  document.getElementById("sendBtn").addEventListener("click", sendMsg);
  document.getElementById("inp").addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); }
  });
});

function authHeaders() {
  return {"Authorization": "Bearer " + STATE.accessToken, "Content-Type": "application/json"};
}

function showTab(tab) {
  clearAuthMessages();
  var tabs = document.querySelectorAll(".auth-tab");
  tabs[0].classList.toggle("active", tab === "login");
  tabs[1].classList.toggle("active", tab === "signup");
  document.getElementById("loginForm").style.display = tab === "login" ? "block" : "none";
  document.getElementById("signupForm").style.display = tab === "signup" ? "block" : "none";
}
function showAuthError(msg) {
  var el = document.getElementById("authError");
  el.textContent = msg; el.style.display = "block";
  document.getElementById("authSuccess").style.display = "none";
}
function showAuthSuccess(msg) {
  var el = document.getElementById("authSuccess");
  el.textContent = msg; el.style.display = "block";
  document.getElementById("authError").style.display = "none";
}
function clearAuthMessages() {
  document.getElementById("authError").style.display = "none";
  document.getElementById("authSuccess").style.display = "none";
}

function doLogin() {
  var email = document.getElementById("loginEmail").value.trim();
  var pass = document.getElementById("loginPassword").value.trim();
  if (!email || !pass) { showAuthError("Email aur password required hai"); return; }
  var btn = document.getElementById("loginBtn");
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>Logging in...';
  clearAuthMessages();
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/auth/login", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onload = function() {
    btn.disabled = false; btn.textContent = "Login";
    try {
      var data = JSON.parse(xhr.responseText);
      if (xhr.status === 200 && data.success) {
        STATE.accessToken = data.access_token;
        STATE.sessionId = data.user.session_id;
        STATE.userEmail = data.user.email;
        localStorage.setItem("mm_access_token", STATE.accessToken);
        localStorage.setItem("mm_session_id", STATE.sessionId);
        localStorage.setItem("mm_user_email", STATE.userEmail);
        showApp(); loadChatList();
      } else {
        showAuthError(data.detail || data.message || "Login failed");
      }
    } catch(e) { showAuthError("Server error. Try again."); }
  };
  xhr.onerror = function() { btn.disabled=false; btn.textContent="Login"; showAuthError("Connection error"); };
  xhr.send(JSON.stringify({email: email, password: pass}));
}

function doSignup() {
  var name = document.getElementById("signupName").value.trim();
  var email = document.getElementById("signupEmail").value.trim();
  var pass = document.getElementById("signupPassword").value.trim();
  if (!email || !pass) { showAuthError("Email aur password required hai"); return; }
  if (pass.length < 6) { showAuthError("Password kam se kam 6 characters ka hona chahiye"); return; }
  var btn = document.getElementById("signupBtn");
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>Creating account...';
  clearAuthMessages();
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/auth/register", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onload = function() {
    btn.disabled = false; btn.textContent = "Create Account";
    try {
      var data = JSON.parse(xhr.responseText);
      if (xhr.status === 200 && data.success) {
        showAuthSuccess("Account created! Ab login karo.");
        setTimeout(function() { showTab("login"); }, 1500);
      } else {
        showAuthError(data.detail || data.message || "Signup failed");
      }
    } catch(e) { showAuthError("Server error. Try again."); }
  };
  xhr.onerror = function() { btn.disabled=false; btn.textContent="Create Account"; showAuthError("Connection error"); };
  xhr.send(JSON.stringify({email: email, password: pass, username: name}));
}

function doLogout() {
  STATE.accessToken = ""; STATE.sessionId = ""; STATE.userEmail = ""; STATE.currentChatId = "";
  localStorage.removeItem("mm_access_token");
  localStorage.removeItem("mm_session_id");
  localStorage.removeItem("mm_user_email");
  showAuth();
}

function showAuth() {
  document.getElementById("authPage").style.display = "flex";
  document.getElementById("app").classList.remove("show");
}
function showApp() {
  document.getElementById("authPage").style.display = "none";
  document.getElementById("app").classList.add("show");
  document.getElementById("userEmailDisplay").textContent = STATE.userEmail;
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

/* ── CHAT HISTORY SIDEBAR ── */
function loadChatList() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/history/list", true);
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.onload = function() {
    if (xhr.status === 401) { doLogout(); return; }
    if (xhr.status !== 200) return;
    try {
      var data = JSON.parse(xhr.responseText);
      renderHistoryList(data.sessions || []);
    } catch(e) { console.error(e); }
  };
  xhr.send();
}

function renderHistoryList(sessions) {
  var list = document.getElementById("historyList");
  list.innerHTML = "";
  if (sessions.length === 0) {
    list.innerHTML = '<div style="padding:10px;font-size:11px;color:#555">No conversations yet</div>';
    return;
  }
  sessions.forEach(function(s) {
    var item = document.createElement("div");
    item.className = "history-item" + (s.chat_id === STATE.currentChatId ? " active" : "");
    item.setAttribute("data-chat-id", s.chat_id);

    var dateStr = "";
    try {
      var d = new Date(s.updated_at);
      dateStr = d.toLocaleDateString() + " " + d.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
    } catch(e) {}

    item.innerHTML =
      '<span class="h-icon">&#128172;</span>' +
      '<div class="h-info">' +
        '<div class="h-title">' + escapeHtml(s.title) + '</div>' +
        '<div class="h-date">' + dateStr + '</div>' +
      '</div>' +
      '<div class="h-actions">' +
        '<button class="h-action-btn" onclick="event.stopPropagation();startRename(\'' + s.chat_id + '\',\'' + escapeHtml(s.title).replace(/'/g,"\\'") + '\')">&#9998;</button>' +
        '<button class="h-action-btn" onclick="event.stopPropagation();confirmDelete(\'' + s.chat_id + '\')">&#128465;</button>' +
      '</div>';

    item.onclick = function() { loadChat(s.chat_id); };
    list.appendChild(item);
  });
}

function escapeHtml(text) {
  var div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function startNewChat() {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/history/new", true);
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.onload = function() {
    if (xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      STATE.currentChatId = data.chat_id;
      document.getElementById("chat").innerHTML =
        '<div class="welcome" id="welcome"><h2>New Chat</h2><p>Ask me anything about your studies!</p></div>';
      loadChatList();
    }
  };
  xhr.send();
}

function loadChat(chatId) {
  STATE.currentChatId = chatId;
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/history/" + chatId + "/messages", true);
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.onload = function() {
    if (xhr.status !== 200) return;
    try {
      var data = JSON.parse(xhr.responseText);
      var chat = document.getElementById("chat");
      chat.innerHTML = "";
      var msgs = data.messages || [];
      if (msgs.length === 0) {
        chat.innerHTML = '<div class="welcome" id="welcome"><h2>' + escapeHtml(data.title || "Chat") + '</h2></div>';
      } else {
        msgs.forEach(function(m) {
          addMsg(m.role === "user" ? "user" : "ai", m.message, m.agent_used || "");
        });
      }
      highlightActiveChat();
    } catch(e) { console.error(e); }
  };
  xhr.send();
}

function highlightActiveChat() {
  document.querySelectorAll(".history-item").forEach(function(el) {
    el.classList.toggle("active", el.getAttribute("data-chat-id") === STATE.currentChatId);
  });
}

function startRename(chatId, currentTitle) {
  var item = document.querySelector('.history-item[data-chat-id="' + chatId + '"] .h-title');
  if (!item) return;
  var input = document.createElement("input");
  input.className = "rename-input";
  input.value = currentTitle;
  item.replaceWith(input);
  input.focus();
  input.select();

  function commit() {
    var newTitle = input.value.trim() || currentTitle;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/history/rename", true);
    xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function() { loadChatList(); };
    xhr.send(JSON.stringify({chat_id: chatId, new_title: newTitle}));
  }
  input.addEventListener("blur", commit);
  input.addEventListener("keydown", function(e) {
    if (e.key === "Enter") { input.blur(); }
  });
}

function confirmDelete(chatId) {
  if (!confirm("Delete this conversation? This cannot be undone.")) return;
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/history/delete", true);
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onload = function() {
    if (STATE.currentChatId === chatId) {
      STATE.currentChatId = "";
      document.getElementById("chat").innerHTML =
        '<div class="welcome" id="welcome"><h2>MENTOR MIND AI</h2><p>Pick a conversation or start new</p></div>';
    }
    loadChatList();
  };
  xhr.send(JSON.stringify({chat_id: chatId}));
}

/* ── DOCUMENT UPLOAD ── */
function uploadFile() {
  var fileInput = document.getElementById("fileInput");
  var file = fileInput.files[0];
  if (!file) return;
  var status = document.getElementById("uploadStatus");
  status.textContent = "Uploading...";
  status.style.color = "#fbbf24";
  var formData = new FormData();
  formData.append("file", file);
  formData.append("session_id", STATE.sessionId);
  formData.append("topic", "");
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/documents/upload", true);
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.onload = function() {
    if (xhr.status === 200) {
      var data = JSON.parse(xhr.responseText);
      if (data.success) {
        status.textContent = "✅ " + file.name;
        status.style.color = "#4ade80";
        addMsg("ai", "✅ " + file.name + " uploaded! Ask: \'What is in my uploaded notes?\'", "Documents");
      } else {
        status.textContent = "❌ " + data.message;
        status.style.color = "#f87171";
      }
    } else {
      status.textContent = "Upload failed";
      status.style.color = "#f87171";
    }
  };
  xhr.onerror = function() { status.textContent = "Upload error"; status.style.color = "#f87171"; };
  xhr.send(formData);
}

/* ── CHAT ── */
function go(text) { document.getElementById("inp").value = text; sendMsg(); }

function addMsg(role, text, tag, elapsed) {
  var chat = document.getElementById("chat");
  var w = document.getElementById("welcome");
  if (w) w.remove();
  var row = document.createElement("div");
  row.className = "row" + (role === "user" ? " me" : "");
  var av = document.createElement("div");
  av.className = "av" + (role === "user" ? " me" : "");
  av.textContent = role === "user" ? (STATE.userEmail ? STATE.userEmail[0].toUpperCase() : "U") : "AI";
  var bub = document.createElement("div");
  bub.className = "bub" + (role === "user" ? " me" : "");
  if (tag) {
    var tg = document.createElement("div");
    tg.className = "atag"; tg.textContent = tag;
    bub.appendChild(tg);
  }
  var c = document.createElement("div");
  c.textContent = text;
  bub.appendChild(c);
  if (elapsed) {
    var ti = document.createElement("div");
    ti.className = "timer"; ti.textContent = "Responded in " + elapsed + "s";
    bub.appendChild(ti);
  }
  row.appendChild(av); row.appendChild(bub);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
  var chat = document.getElementById("chat");
  var row = document.createElement("div");
  row.className = "row"; row.id = "typing";
  row.innerHTML = '<div class="av">AI</div><div class="bub"><div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div><div class="tinfo">Agents working...</div><div class="pbar"><div class="pfill"></div></div></div>';
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}
function hideTyping() {
  var t = document.getElementById("typing");
  if (t) t.remove();
}

function sendMsg() {
  var inp = document.getElementById("inp");
  var sBtn = document.getElementById("sendBtn");
  var text = inp.value.trim();
  if (!text || sBtn.disabled) return;
  if (!STATE.accessToken) { doLogout(); return; }
  addMsg("user", text);
  inp.value = "";
  sBtn.disabled = true; sBtn.textContent = "...";
  showTyping();
  STATE.t0 = Date.now();
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/chat/", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Authorization", "Bearer " + STATE.accessToken);
  xhr.timeout = 90000;
  xhr.onload = function() {
    hideTyping();
    var elapsed = ((Date.now() - STATE.t0) / 1000).toFixed(1);
    if (xhr.status === 401) { doLogout(); return; }
    if (xhr.status === 200) {
      try {
        var data = JSON.parse(xhr.responseText);
        var route = data.route || {};
        var tag = data.agents_used && data.agents_used.length ? "Agents: " + data.agents_used.join(" + ") + (data.topic ? " | Topic: " + data.topic : "") : "";
        addMsg("ai", data.response, tag, elapsed);
        if (data.chat_id) {
          STATE.currentChatId = data.chat_id;
          loadChatList();
        }
      } catch(e) { addMsg("ai", "Response read nahi hui. Try again."); }
    } else {
      try {
        var err = JSON.parse(xhr.responseText);
        addMsg("ai", "Error: " + (err.detail || "Server error " + xhr.status));
      } catch(e) { addMsg("ai", "Server error " + xhr.status); }
    }
    sBtn.disabled = false; sBtn.textContent = "Send"; inp.focus();
  };
  xhr.onerror = function() {
    hideTyping();
    addMsg("ai", "Connection lost. Refresh karein.");
    sBtn.disabled = false; sBtn.textContent = "Send";
  };
  xhr.ontimeout = function() {
    hideTyping();
    addMsg("ai", "Timeout. Try a simpler question.");
    sBtn.disabled = false; sBtn.textContent = "Send";
  };
  xhr.send(JSON.stringify({message: text, session_id: STATE.sessionId, chat_id: STATE.currentChatId}));
}
</script>
</body>
</html>"""
