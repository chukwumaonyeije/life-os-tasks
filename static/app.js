async function loadTasks(){
  const r = await fetch('/api/tasks?status=active');
  const tasks = await r.json();
  const el = document.getElementById("tasks");
  el.innerHTML="";
  
  if (tasks.length === 0) {
    el.innerHTML = '<div style="color:#9ca3af;">No active tasks</div>';
    return;
  }
  
  tasks.forEach(t=>{
    const d=document.createElement("div");
    d.className = "task-item";
    d.id = `task-${t.id}`;
    
    const completedClass = t.status === "completed" ? "task-completed" : "";
    
    d.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px;">
        <input type="checkbox" onchange="toggleTaskComplete('${t.id}', this.checked)" ${t.status === "completed" ? "checked" : ""}>
        <div style="flex:1;" class="${completedClass}">
          <strong>${t.title}</strong>
          <span class="badge approved">${t.priority}</span>
          ${t.status !== "active" ? `<span class="badge ${t.status}">${t.status.toUpperCase()}</span>` : ""}
        </div>
      </div>
      <div style="margin-top:.5rem; color:#6b7280; font-size:.9rem;">
        ${t.description || ""}
      </div>
      <div class="meta">
        source: ${t.source || "manual"}
        ${t.completed_at ? ` · completed ${formatDate(t.completed_at)}` : ""}
      </div>
    `;
    el.appendChild(d);
  });
}

async function addTask(){
  const title=document.getElementById("title").value;
  if(!title) return;
  await fetch('/api/tasks',{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({title})
  });
  document.getElementById("title").value = "";
  loadTasks();
}

async function loadInbox(){
  const r = await fetch('/api/inbox');
  const items = await r.json();
  const el = document.getElementById("inbox");
  el.innerHTML="";
  items.forEach(ev=>{
    const d=document.createElement("div");
    d.textContent = `[${ev.source}] ${ev.payload}`;
    el.appendChild(d);
  });
}

async function addEvent(){
  const payload=document.getElementById("payload").value;
  const source=document.getElementById("source").value;
  if(!payload) return;
  await fetch('/api/inbox',{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({payload, source})
  });
  document.getElementById("payload").value = "";
  loadInbox();
}

async function loadReview(){
  const r = await fetch('/api/review');
  const items = await r.json();
  const el = document.getElementById("review");
  el.innerHTML="";
  
  if (items.length === 0) {
    el.innerHTML = '<div style="color:#9ca3af;">No pending candidates</div>';
    return;
  }
  
  items.forEach(c=>{
    const d=document.createElement("div");
    d.className = "review-item";
    d.id = `candidate-${c.id}`;
    
    // Build AI metadata display
    let aiInfo = '';
    if (c.ai_metadata) {
      const confidence = Math.round(c.ai_metadata.confidence * 100);
      aiInfo = `
        <div class="ai-badge">
          <span class="badge ai">🤖 ${c.ai_metadata.provider} (${c.ai_metadata.model})</span>
          <span class="confidence">Confidence: ${confidence}%</span>
        </div>
        <details class="rationale-expand">
          <summary>Why suggested</summary>
          <p>${c.ai_metadata.rationale}</p>
        </details>
      `;
    }
    
    d.innerHTML = `
      <div style="display:flex; align-items:center; justify-content:space-between;">
        <div>
          <strong>${c.title}</strong>
          <span class="badge ${c.priority}">${c.priority.toUpperCase()}</span>
          <span class="badge pending">PENDING</span>
        </div>
      </div>
      ${c.description ? `<div style="margin-top:0.5rem; color:#4b5563;">${c.description}</div>` : ''}
      ${aiInfo}
      <div style="margin-top:0.75rem;">
        <button onclick="approveCandidate('${c.id}')">Approve</button>
        <button onclick="rejectCandidate('${c.id}')" style="background:#6b7280;">Reject</button>
      </div>
      <div class="meta">Created ${formatDate(c.created_at)}</div>
    `;
    el.appendChild(d);
  });
}

async function loadApproved(){
  const r = await fetch('/api/review/approved');
  const items = await r.json();
  const el = document.getElementById("approved");
  el.innerHTML="";
  
  if (items.length === 0) {
    el.innerHTML = '<div style="color:#9ca3af; font-size:.9rem;">No recent approvals</div>';
    return;
  }
  
  items.forEach(c=>{
    const d=document.createElement("div");
    d.innerHTML = `
      <div>
        ${c.title}
        <span class="badge approved">✓ APPROVED</span>
      </div>
      <div class="meta">
        ${formatDate(c.created_at)}
      </div>
    `;
    el.appendChild(d);
  });
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  
  return date.toLocaleDateString();
}

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 2500);
}

async function approveCandidate(id) {
  const item = document.getElementById(`candidate-${id}`);
  if (item) {
    item.classList.add("processing");
  }

  try {
    const res = await fetch(`/api/review/${id}/approve`, { method: "POST" });
    const data = await res.json();

    if (data.error) {
      showToast(data.message || "Approval failed", "error");
      if (item) {
        item.classList.remove("processing");
      }
      return;
    }

    showToast(data.message || "Task approved", "success");
    await loadReview();
    await loadApproved();
    await loadTasks();
  } catch (err) {
    showToast("Approval failed", "error");
    if (item) {
      item.classList.remove("processing");
    }
  }
}

async function rejectCandidate(id) {
  const item = document.getElementById(`candidate-${id}`);
  if (item) {
    item.classList.add("processing");
  }

  try {
    const res = await fetch(`/api/review/${id}/reject`, { method: "POST" });
    const data = await res.json();

    if (data.error) {
      showToast(data.message || "Rejection failed", "error");
      if (item) {
        item.classList.remove("processing");
      }
      return;
    }

    showToast(data.message || "Candidate rejected", "success");
    await loadReview();
    await loadApproved();
  } catch (err) {
    showToast("Rejection failed", "error");
    if (item) {
      item.classList.remove("processing");
    }
  }
}

async function toggleTaskComplete(taskId, checked) {
  const endpoint = checked ? "complete" : "reactivate";
  
  try {
    const res = await fetch(`/api/tasks/${taskId}/${endpoint}`, { method: "POST" });
    const data = await res.json();
    
    if (data.error) {
      showToast(data.message || "Action failed", "error");
      return;
    }
    
    showToast(data.message || "Task updated", "success");
    await loadTasks();
  } catch (err) {
    showToast("Action failed", "error");
  }
}

async function loadAll(){
  await loadInbox();
  await loadReview();
  await loadApproved();
  await loadTasks();
}

loadAll();
