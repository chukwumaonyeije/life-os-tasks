async function loadTasks(){
  const r = await fetch('/api/tasks?status=active');
  const tasks = await r.json();
  const el = document.getElementById("tasks");
  el.innerHTML="";
  
  if (!tasks || tasks.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'card';
    empty.innerHTML = '<div style="color:#94a3b8">No active tasks</div>';
    el.appendChild(empty);
    return;
  }

  tasks.forEach(t=>{
    const d=document.createElement("div");
    d.className = "card task-item";
    d.id = `task-${t.id}`;

    const completedClass = t.status === "completed" ? "task-completed" : "";

    d.innerHTML = `
      <div style="display:flex; align-items:center; gap:12px; width:100%">
        <input aria-label="Mark task complete" type="checkbox" onchange="toggleTaskComplete('${t.id}', this.checked)" ${t.status === "completed" ? "checked" : ""}>
        <div style="flex:1;">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div class="${completedClass}"><strong>${escapeHtml(t.title)}</strong></div>
            <div>
              ${t.priority ? `<span class="badge ${t.priority}">${escapeHtml(t.priority)}</span>` : ''}
              ${t.status && t.status !== 'active' ? `<span class="badge ${t.status}">${escapeHtml(t.status.toUpperCase())}</span>` : ''}
            </div>
          </div>

          ${t.description ? `<div class="meta" style="margin-top:6px">${escapeHtml(t.description)}</div>` : ''}
          <div class="meta" style="margin-top:8px">source: ${escapeHtml(t.source || 'manual')}${t.completed_at ? ` · completed ${formatDate(t.completed_at)}` : ''}</div>
        </div>
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
  if (!items || items.length === 0) {
    el.innerHTML = '<div class="card">No inbox items</div>';
    return;
  }

  items.forEach(ev=>{
    const d=document.createElement("div");
    d.className = 'card';
    d.innerHTML = `<div style="flex:1"><div><strong>[${escapeHtml(ev.source||'manual')}]</strong> ${escapeHtml(ev.payload||'')}</div><div class="meta">${formatDate(ev.created_at||ev.ingest_time||new Date())}</div></div>`;
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
    el.innerHTML = '<div class="card">No pending candidates</div>';
    return;
  }
  
  items.forEach(c=>{
    const d=document.createElement("div");
    d.className = "card review-item";
    d.id = `candidate-${c.id}`;

    // Build AI metadata display
    let aiInfo = '';
    if (c.ai_metadata) {
      const confidence = Math.round((c.ai_metadata.confidence || 0) * 100);
      aiInfo = `
        <div class="ai-badge">
          <span class="badge ai">🤖 ${escapeHtml(c.ai_metadata.provider||'AI')}</span>
          <span class="confidence">Confidence: ${confidence}%</span>
        </div>
        <details class="rationale-expand">
          <summary>Why suggested</summary>
          <p>${escapeHtml(c.ai_metadata.rationale||'')}</p>
        </details>
      `;
    }

    d.innerHTML = `
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
        <div>
          <strong>${escapeHtml(c.title)}</strong>
          ${c.priority ? `<span class="badge ${c.priority}">${escapeHtml(c.priority.toUpperCase())}</span>` : ''}
          <span class="badge pending">PENDING</span>
        </div>
      </div>
      ${c.description ? `<div style="margin-top:0.5rem; color:#4b5563;">${escapeHtml(c.description)}</div>` : ''}
      ${aiInfo}
      <div style="margin-top:0.75rem; display:flex; gap:8px;">
        <button class="btn" onclick="approveCandidate('${c.id}')">Approve</button>
        <button class="btn" style="background:#6b7280;" onclick="rejectCandidate('${c.id}')">Reject</button>
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

function escapeHtml(str){
  if (!str && str !== 0) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
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

document.addEventListener('DOMContentLoaded', function(){
  loadAll();
  // Export button
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) exportBtn.addEventListener('click', async ()=>{
    exportBtn.disabled = true;
    try{
      const res = await fetch('/api/export');
      if(!res.ok) throw new Error('Export failed');
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lifeos-export-${new Date().toISOString().slice(0,19)}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showToast('Export downloaded', 'success');
    }catch(e){
      showToast('Export failed', 'error');
    }finally{ exportBtn.disabled = false }
  });

  // Import file handler
  const importFile = document.getElementById('import-file');
  if (importFile) importFile.addEventListener('change', async (evt)=>{
    const f = evt.target.files && evt.target.files[0];
    if(!f) return;

    // First request a preview summary
    const previewForm = new FormData();
    previewForm.append('file', f, f.name);
    try{
      const previewRes = await fetch('/api/import/preview', {method:'POST', body: previewForm});
      const preview = await previewRes.json();
      if(!previewRes.ok){
        showToast(preview.detail || 'Preview failed', 'error');
        importFile.value = '';
        return;
      }

      // Build a concise human message
      const counts = preview.preview.counts;
      const collisions = preview.collisions;
      let msg = `Import preview:\n`;
      msg += ` - raw_events: ${counts.raw_events} (existing: ${collisions.raw_events.length})\n`;
      msg += ` - task_candidates: ${counts.task_candidates} (existing: ${collisions.task_candidates.length})\n`;
      msg += ` - tasks: ${counts.tasks} (existing: ${collisions.tasks.length})\n`;
      msg += ` - review_actions: ${counts.review_actions} (existing: ${collisions.review_actions.length})\n`;
      msg += ` - ai_suggestions: ${counts.ai_suggestions} (existing: ${collisions.ai_suggestions.length})\n\n`;
      msg += `Samples:\n`;
      if(preview.preview.samples.task_candidates.length){
        preview.preview.samples.task_candidates.forEach(s=>{ msg += ` • candidate: ${s.id} ${s.title || ''}\n` });
      }
      if(preview.preview.samples.tasks.length){
        preview.preview.samples.tasks.forEach(s=>{ msg += ` • task: ${s.id} ${s.title || ''}\n` });
      }

      msg += `\nProceed with import? This will merge records and may overwrite fields of existing IDs.`;

      // Show modal preview instead of browser confirm
      showImportModal(preview, f);
    }catch(e){
      showToast('Import failed', 'error');
    } finally { importFile.value = '' }
  });
});

let _pendingImportFile = null;

function showImportModal(previewPayload, file){
  _pendingImportFile = file;
  const modal = document.getElementById('import-modal');
  const summary = document.getElementById('preview-summary');
  const collisions = document.getElementById('preview-collisions');
  const samples = document.getElementById('preview-samples');
  if(!modal || !summary) return;

  const counts = previewPayload.preview.counts;
  summary.innerHTML = `
    <div style="display:flex; justify-content:space-between; gap:12px;">
      <div class="preview-grid">
        <div class="preview-item">Raw events<br><strong>${counts.raw_events}</strong></div>
        <div class="preview-item">Candidates<br><strong>${counts.task_candidates}</strong></div>
        <div class="preview-item">Tasks<br><strong>${counts.tasks}</strong></div>
      </div>
    </div>
    <div style="margin-top:8px; color:var(--muted); font-size:.95rem">Imported at: ${new Date().toLocaleString()}</div>
  `;

  // collisions
  collisions.innerHTML = '';
  const col = previewPayload.collisions || {};
  Object.keys(col).forEach(k=>{
    if((col[k] || []).length === 0) return;
    const el = document.createElement('div');
    el.innerHTML = `<strong>${k}:</strong>`;
    const ul = document.createElement('ul'); ul.className = 'collision-list';
    col[k].slice(0,10).forEach(id=>{ const li = document.createElement('li'); li.textContent = id; ul.appendChild(li)});
    el.appendChild(ul);
    collisions.appendChild(el);
  });

  // samples
  samples.innerHTML = '';
  const s = previewPayload.preview.samples || {};
  Object.keys(s).forEach(k=>{
    const arr = s[k] || [];
    if(arr.length === 0) return;
    const sec = document.createElement('div');
    sec.innerHTML = `<strong>${k}</strong>`;
    arr.forEach(it=>{
      const p = document.createElement('div'); p.style.padding='6px 0'; p.style.borderBottom='1px solid #f1f5f9'; p.textContent = Object.values(it).filter(Boolean).join(' — ');
      sec.appendChild(p);
    });
    samples.appendChild(sec);
  });

    // diffs
    const diffsContainer = document.getElementById('preview-diffs');
    if(diffsContainer) diffsContainer.innerHTML = '';
    const diffs = previewPayload.preview.diffs || {};
    Object.keys(diffs).forEach(collName=>{
      const coll = diffs[collName];
      if(!coll || Object.keys(coll).length === 0) return;
      const title = document.createElement('div');
      title.innerHTML = `<h4 style="margin-top:12px">Field differences: ${collName}</h4>`;
      if(diffsContainer) diffsContainer.appendChild(title);
      Object.keys(coll).forEach(id=>{
        const entry = coll[id];
        const entDiv = document.createElement('div'); entDiv.style.marginTop='8px';
        entDiv.innerHTML = `<strong>${id}</strong>`;
        const table = document.createElement('table'); table.style.width='100%'; table.style.borderCollapse='collapse'; table.style.marginTop='6px';
        const thead = document.createElement('thead'); thead.innerHTML = `<tr><th style="text-align:left;padding:6px;border-bottom:1px solid #e6eef8">Field</th><th style="text-align:left;padding:6px;border-bottom:1px solid #e6eef8">Existing</th><th style="text-align:left;padding:6px;border-bottom:1px solid #e6eef8">Incoming</th></tr>`;
        table.appendChild(thead);
        const tbody = document.createElement('tbody');
        Object.keys(entry).forEach(field=>{
          const row = document.createElement('tr'); row.className = 'diff-row';
          const a = document.createElement('td'); a.style.padding='6px'; a.textContent = field;
          row.dataset.field = field;

          function renderValue(val){
            const cell = document.createElement('td'); cell.style.padding='6px';
            const pre = document.createElement('pre'); pre.className = 'diff-value collapsed';
            let text;
            try{
              if (val === null || val === undefined) text = String(val);
              else if (typeof val === 'object') text = JSON.stringify(val, null, 2);
              else text = String(val);
            }catch(e){ text = String(val); }
            pre.textContent = text;

            const btn = document.createElement('button'); btn.className = 'expand-btn'; btn.type='button'; btn.setAttribute('aria-expanded','false'); btn.textContent = 'Expand';
            btn.addEventListener('click', ()=>{
              const expanded = btn.getAttribute('aria-expanded') === 'true';
              if (expanded){ pre.classList.add('collapsed'); btn.setAttribute('aria-expanded','false'); btn.textContent = 'Expand'; }
              else { pre.classList.remove('collapsed'); btn.setAttribute('aria-expanded','true'); btn.textContent = 'Collapse'; }
            });

            cell.appendChild(pre);
            cell.appendChild(btn);
            return cell;
          }

          const b = renderValue(entry[field].existing);
          const c = renderValue(entry[field].incoming);

          // add override selector to the leftmost cell
          const select = document.createElement('select');
          select.innerHTML = '<option value="incoming">Use incoming</option><option value="existing">Keep existing</option>';
          select.className = 'override-select';
          select.style.marginLeft = '8px';
          select.setAttribute('aria-label', `Override ${field}`);
          a.appendChild(select);

          row.appendChild(a); row.appendChild(b); row.appendChild(c);
          tbody.appendChild(row);
        });
        table.appendChild(tbody);
        entDiv.appendChild(table);
        if(diffsContainer) diffsContainer.appendChild(entDiv);
      });
    });

  // show modal
  modal.classList.remove('hidden');
  // hide the main app to assist screen readers
  const appRoot = document.querySelector('.app');
  if (appRoot) appRoot.setAttribute('aria-hidden', 'true');

  // announce and prepare focus trap
  const announcer = document.getElementById('modal-announcer');
  if (announcer) announcer.textContent = 'Import preview opened. Press Tab to navigate, Escape to close.';

  // Save previously focused element
  const previouslyFocused = document.activeElement;

  // Make modal panel focusable and focus it
  const panel = modal.querySelector('.modal-panel');
  if (panel) {
    panel.setAttribute('tabindex', '-1');
  }

  // Create and activate focus trap (uses global createFocusTrap)
  let currentTrap = null;
  try{
    currentTrap = window.createFocusTrap(panel, { onDeactivate: onCancel, returnFocus: previouslyFocused });
    currentTrap.activate(panel);
  }catch(e){ /* graceful fallback */ }

  // wire buttons
  const cancelBtn = document.getElementById('modal-cancel');
  const confirmBtn = document.getElementById('modal-confirm');
  const closeBtn = document.getElementById('modal-close');
  const backdrop = document.getElementById('modal-backdrop');

  function closeModal(){
    modal.classList.add('hidden');
    _pendingImportFile = null;
    // restore aria-hidden and focus
    if (appRoot) appRoot.removeAttribute('aria-hidden');
    try{ if (previouslyFocused && typeof previouslyFocused.focus === 'function') previouslyFocused.focus(); }catch(e){}

    cancelBtn.removeEventListener('click', onCancel);
    confirmBtn.removeEventListener('click', onConfirm);
    closeBtn.removeEventListener('click', onCancel);
    backdrop.removeEventListener('click', onCancel);
    if (currentTrap && typeof currentTrap.deactivate === 'function'){
      try{ currentTrap.deactivate(); }catch(e){}
    }
    if (announcer) announcer.textContent = '';
  }

  function onCancel(e){ e && e.preventDefault(); closeModal(); }

  async function onConfirm(e){
    e && e.preventDefault();
    confirmBtn.disabled = true; cancelBtn.disabled = true;
    try{
      const form = new FormData();
      form.append('file', _pendingImportFile, _pendingImportFile.name);

      // collect overrides from diff table
      const overrides = {};
      const diffsContainerLocal = document.getElementById('preview-diffs');
      if (diffsContainerLocal){
        // find each diff entry
        const entries = diffsContainerLocal.querySelectorAll('div[data-coll]');
        // fallback: we structured entries under elements with data attributes on parent when created
      }

      // Alternative collection: iterate over table rows and collect selects
      const tables = modal.querySelectorAll('table');
      tables.forEach(tbl=>{
        const collSection = tbl.closest('[data-coll]');
      });

      // Fallback: iterate over all rows with data-field and find ancestor with coll/id
      const rows = modal.querySelectorAll('.diff-row');
      rows.forEach(r=>{
        const field = r.dataset.field;
        // find the parent entry that has data-id and data-coll
        let parent = r.closest('div[data-id]') || r.closest('div[data-coll]');
        if (!parent){
          // try to climb until a parent with strong id text
          parent = r.parentElement;
        }
        // recover collName and id from surrounding markup: we set them on entDiv when creating diffs
        const collName = parent ? parent.dataset.coll : null;
        const id = parent ? parent.dataset.id : null;
        if (!collName || !id) return;
        const sel = r.querySelector('.override-select');
        const choice = sel ? sel.value : 'incoming';
        overrides[collName] = overrides[collName] || {};
        overrides[collName][id] = overrides[collName][id] || {};
        overrides[collName][id][field] = choice;
      });

      if (Object.keys(overrides).length > 0){
        form.append('overrides', JSON.stringify(overrides));
      }

      const res = await fetch('/api/import', {method:'POST', body: form});
      const data = await res.json();
      if(!res.ok){ showToast(data.detail || 'Import failed', 'error'); }
      else { showToast('Import complete', 'success'); loadAll(); }
    }catch(err){ showToast('Import failed', 'error'); }
    finally{ confirmBtn.disabled = false; cancelBtn.disabled = false; closeModal(); }
  }

  function onKey(e){ if(e.key === 'Escape') onCancel(); }

  // focus trap handler
  function onKeyDown(e){
    if (e.key === 'Escape') { onCancel(); return; }

    if (e.key === 'Tab') {
      const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      const focusableEls = Array.prototype.slice.call(focusable).filter(function(el){ return !el.hasAttribute('disabled') && el.offsetParent !== null; });
      if (focusableEls.length === 0) { e.preventDefault(); return; }
      const firstEl = focusableEls[0];
      const lastEl = focusableEls[focusableEls.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === firstEl) {
          e.preventDefault();
          lastEl.focus();
        }
      } else {
        if (document.activeElement === lastEl) {
          e.preventDefault();
          firstEl.focus();
        }
      }
    }
  }

  cancelBtn.addEventListener('click', onCancel);
  closeBtn.addEventListener('click', onCancel);
  backdrop.addEventListener('click', onCancel);
  confirmBtn.addEventListener('click', onConfirm);
  document.addEventListener('keydown', onKeyDown);
}
