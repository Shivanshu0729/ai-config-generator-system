const API_BASE = 'http://127.0.0.1:8001/api/v1';

const EXAMPLE_PROMPTS = {
  crm: 'Build a CRM with login, contacts list, lead pipeline, dashboard with analytics, role-based access (admin, sales rep, manager), and a premium plan with Stripe payments. Admins can see full analytics. Sales reps can only view their own contacts.',
  pm: 'Build a project management tool with team workspaces, task boards in kanban style, deadlines, file attachments, notifications, time tracking per task, and a reporting dashboard for managers.',
  ecom: 'Build an e-commerce store with product catalog, category filtering, shopping cart, Stripe checkout, order history, inventory management, and an admin dashboard with revenue analytics.',
  blog: 'Build a blog platform with rich text post creation, categories and tags, comments with moderation, post likes, user profiles, and an admin panel for content moderation. Authors can only edit their own posts.',
  vague: 'Make something cool'
};

let fullConfig = {};
let isRunning = false;

window.addEventListener('DOMContentLoaded', () => {
  setupCharCounter();
  setupChips();
  setupTabs();
  setupNavScroll();
  resetAllStages();
  setMetrics(null, null, null);
});

function setupCharCounter() {
  const textarea = document.getElementById('prompt');
  const charCount = document.getElementById('charCount');
  const progressFill = document.getElementById('progressFill');
  const charHint = document.getElementById('charHint');

  textarea.addEventListener('input', () => {
    const length = textarea.value.length;
    charCount.textContent = `${length} / 800`;
    progressFill.style.width = `${Math.min(100, (length / 800) * 100)}%`;

    if (length > 300) {
      charHint.textContent = 'Good detail';
    } else if (length > 100) {
      charHint.textContent = 'Nice start';
    } else if (length > 0) {
      charHint.textContent = 'Add more specifics';
    } else {
      charHint.textContent = '';
    }
  });

  textarea.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      runPipeline();
    }
  });
}

function setupChips() {
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const key = chip.getAttribute('data-example');
      const textarea = document.getElementById('prompt');
      textarea.value = EXAMPLE_PROMPTS[key] || '';
      textarea.dispatchEvent(new Event('input'));
      textarea.focus();
    });
  });
}

function setupTabs() {
  document.querySelectorAll('.output-tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });
}

function setupNavScroll() {
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 16);
  });
}

function switchTab(name) {
  document.querySelectorAll('.output-tab').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

  const activeTab = document.querySelector(`.output-tab[data-tab="${name}"]`);
  const activePanel = document.getElementById(`tab-${name}`);

  if (activeTab) activeTab.classList.add('active');
  if (activePanel) activePanel.classList.add('active');
}

function setStage(index, state) {
  const indicator = document.getElementById(`ind-${index}`);
  const row = document.getElementById(`stage-${index}`);
  const badge = document.getElementById(`badge-${index}`);

  if (!indicator || !row || !badge) return;

  indicator.className = `stage-indicator ${state}`;
  row.className = `stage-row ${state}`;

  const labels = {
    idle: '',
    active: 'Running...',
    done: 'Done',
    error: 'Failed'
  };

  badge.className = `stage-badge ${state}`;
  badge.textContent = labels[state] || '';
}

function resetAllStages() {
  [0, 1, 2, 3].forEach(index => setStage(index, 'idle'));
}

function setMetrics(latency, retries, score) {
  document.getElementById('mLatency').textContent = Number.isFinite(latency) ? latency.toFixed(1) : '—';
  document.getElementById('mRetries').textContent = Number.isFinite(retries) ? String(retries) : '—';
  document.getElementById('mScore').textContent = Number.isFinite(score) ? `${score}%` : '—';
}

function setLoading(loading) {
  const button = document.getElementById('generateBtn');

  isRunning = loading;
  button.disabled = loading;

  if (loading) {
    button.innerHTML = '<span class="btn-spinner"></span><span id="btnLabel">Compiling...</span>';
  } else {
    button.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg><span id="btnLabel">Compile application</span>';
  }
}

function showError(message) {
  const errorContainer = document.getElementById('errorContainer');
  errorContainer.textContent = message;
  errorContainer.classList.remove('hidden');
}

function clearError() {
  document.getElementById('errorContainer').classList.add('hidden');
}

function clearAll() {
  const prompt = document.getElementById('prompt');
  prompt.value = '';
  prompt.dispatchEvent(new Event('input'));
  clearError();
  resetAllStages();
  setMetrics(null, null, null);
  fullConfig = {};

  ['overview', 'schemas', 'validation', 'assumptions', 'raw'].forEach(name => {
    const idle = document.getElementById(`${name}-idle`);
    const content = document.getElementById(`${name}-content`);
    if (idle) idle.classList.remove('hidden');
    if (content) content.classList.add('hidden');
  });

  document.getElementById('overview-content').classList.add('hidden');
  document.getElementById('overview-idle').classList.remove('hidden');
  document.getElementById('prompt').focus();
  switchTab('overview');
}

async function runPipeline() {
  if (isRunning) return;

  const prompt = document.getElementById('prompt').value.trim();
  clearError();

  if (!prompt) {
    showError('Please enter an application description before compiling.');
    return;
  }

  if (prompt.length < 10) {
    showError('Description must be at least 10 characters.');
    return;
  }

  setLoading(true);
  resetAllStages();
  setStage(0, 'active');
  switchTab('overview');

  const startTime = performance.now();

  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt })
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const payload = await response.json();

    if (!payload.success) {
      setStage(0, 'error');
      showError(payload.error || 'Generation failed.');
      return;
    }

    const config = payload.config || {};
    const metrics = payload.metrics || {};

    fullConfig = config;

    [0, 1, 2, 3].forEach(index => setStage(index, 'done'));

    const latency = typeof metrics.latency_seconds === 'number'
      ? metrics.latency_seconds
      : (performance.now() - startTime) / 1000;
    const retries = typeof metrics.api_retries === 'number' ? metrics.api_retries : 0;
    const score = typeof metrics.quality_score === 'number' ? metrics.quality_score : 100;

    setMetrics(latency, retries, score);
    renderOverview(config, metrics);
    renderSchemas(config);
    renderValidation(config, metrics);
    renderAssumptions(config);
    renderRaw(config);
    switchTab('overview');
  } catch (error) {
    setStage(0, 'error');
    showError(error.message || 'Unexpected error while generating the application.');
  } finally {
    setLoading(false);
  }
}

function renderOverview(config, metrics) {
  const overviewIdle = document.getElementById('overview-idle');
  const overviewContent = document.getElementById('overview-content');
  const intentSummary = document.getElementById('intentSummary');
  const intentTags = document.getElementById('intentTags');
  const archSummary = document.getElementById('archSummary');

  overviewIdle.classList.add('hidden');
  overviewContent.classList.remove('hidden');

  const intent = normalizeIntent(config);
  const architecture = normalizeArchitecture(config);

  intentSummary.textContent = `${intent.appType} · ${intent.features.join(', ') || 'Generated application'}`;

  const tags = [];
  if (intent.authRequired) tags.push(tag('Auth required', 'tag-auth'));
  if (intent.paymentRequired) tags.push(tag('Payments', 'tag-api'));
  if (intent.roles.length) tags.push(tag(`Roles: ${intent.roles.join(', ')}`, 'tag-ui'));
  if (intent.entities.length) tags.push(tag(`${intent.entities.length} entities`, 'tag-db'));
  if (intent.services.length) tags.push(tag(intent.services.join(', '), 'tag-third'));

  intentTags.innerHTML = '';
  tags.forEach(item => intentTags.appendChild(item));

  archSummary.innerHTML = [
    row('Pages', architecture.pages.join(', ') || '—'),
    row('Services', architecture.services.join(', ') || '—'),
    row('Third-party', architecture.thirdParty.join(', ') || 'none'),
    row('Execution', formatExecution(metrics.execution))
  ].join('');
}

function renderSchemas(config) {
  document.getElementById('schemas-idle').classList.add('hidden');
  document.getElementById('schemas-content').classList.remove('hidden');

  const schemas = normalizeSchemas(config);
  document.getElementById('uiSchemaOut').textContent = JSON.stringify(schemas.ui, null, 2);
  document.getElementById('apiSchemaOut').textContent = JSON.stringify(schemas.api, null, 2);
  document.getElementById('dbSchemaOut').textContent = JSON.stringify(schemas.db, null, 2);
  document.getElementById('authSchemaOut').textContent = JSON.stringify(schemas.auth, null, 2);
}

function renderValidation(config, metrics) {
  document.getElementById('validation-idle').classList.add('hidden');
  document.getElementById('validation-content').classList.remove('hidden');

  const list = document.getElementById('validationList');
  const checks = normalizeValidation(config, metrics);
  const labels = {
    pass: 'Pass',
    fail: 'Fail',
    warn: 'Warning',
    repair: 'Auto-repaired'
  };

  if (checks.length === 0) {
    list.innerHTML = '<div class="validation-item pass"><span class="v-label">Pass</span><span class="v-msg">No validation data returned, but the request completed successfully.</span></div>';
    return;
  }

  list.innerHTML = checks.map(check => `
    <div class="validation-item ${check.type}">
      <span class="v-label">${labels[check.type] || 'Check'}</span>
      <span class="v-msg">${escapeHtml(check.msg)}</span>
    </div>
  `).join('');
}

function renderAssumptions(config) {
  document.getElementById('assumptions-idle').classList.add('hidden');
  document.getElementById('assumptions-content').classList.remove('hidden');

  const list = document.getElementById('assumptionsList');
  const assumptions = normalizeAssumptions(config);

  if (assumptions.length === 0) {
    list.innerHTML = '<div class="assumption-item"><strong>No assumptions needed</strong> — the prompt was fully specified.</div>';
    return;
  }

  list.innerHTML = assumptions.map(item => `
    <div class="assumption-item">
      <span class="assumption-label">${escapeHtml(item.label)}</span>
      <span class="assumption-text">${escapeHtml(item.text)}</span>
    </div>
  `).join('');
}

function renderRaw(config) {
  document.getElementById('raw-idle').classList.add('hidden');
  document.getElementById('raw-content').classList.remove('hidden');
  document.getElementById('rawJsonOut').textContent = JSON.stringify(config, null, 2);
}

function copyFullConfig() {
  if (!fullConfig || Object.keys(fullConfig).length === 0) return;
  copyText(JSON.stringify(fullConfig, null, 2), button => {
    if (!button) return;
    const original = button.textContent;
    button.textContent = 'Copied!';
    button.classList.add('copied');
    setTimeout(() => {
      button.textContent = original;
      button.classList.remove('copied');
    }, 1600);
  }, 'copyAllBtn');
}

function copySchema(elementId) {
  const element = document.getElementById(elementId);
  const button = element?.closest('.schema-block')?.querySelector('.btn-copy-schema');
  if (!element) return;

  copyText(element.textContent, btn => {
    if (!btn) return;
    const original = btn.textContent;
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = original;
      btn.classList.remove('copied');
    }, 1600);
  }, button);
}

function copyText(text, onSuccess, button) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => onSuccess(resolveButton(button)));
    return;
  }

  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();

  try {
    document.execCommand('copy');
    onSuccess(resolveButton(button));
  } finally {
    document.body.removeChild(textarea);
  }
}

function resolveButton(button) {
  if (!button) return null;
  if (typeof button === 'string') return document.getElementById(button);
  return button;
}

function tag(text, className) {
  const span = document.createElement('span');
  span.className = `output-tag ${className}`;
  span.textContent = text;
  return span;
}

function row(label, value) {
  return `<div class="arch-row"><span class="arch-label">${label}</span><span class="arch-value">${escapeHtml(value)}</span></div>`;
}

function formatExecution(execution) {
  if (!execution || typeof execution !== 'object') return '—';
  const status = execution.status || 'unknown';
  const message = execution.message || execution.error || 'No execution details';
  return `${status} · ${message}`;
}

function normalizeIntent(config) {
  const source = config.intent || config.parsed_intent || config;
  return {
    appType: source.app_type || source.app_name || 'Application',
    features: toArray(source.core_features || source.features || source.entities).map(item => extractName(item)).filter(Boolean).slice(0, 6),
    authRequired: Boolean(source.auth_required ?? source.auth?.required ?? true),
    paymentRequired: Boolean(source.payment_required),
    roles: toArray(source.roles).map(extractName).filter(Boolean),
    entities: toArray(source.entities).map(extractName).filter(Boolean),
    services: toArray(source.third_party_services || source.third_party).map(extractName).filter(Boolean)
  };
}

function normalizeArchitecture(config) {
  const source = config.architecture || config.design || {};
  return {
    pages: toArray(source.pages).map(item => extractName(item?.name || item?.route || item)).filter(Boolean),
    services: toArray(source.services).map(item => extractName(item?.name || item)).filter(Boolean),
    thirdParty: toArray(source.third_party).map(extractName).filter(Boolean)
  };
}

function normalizeSchemas(config) {
  return {
    ui: config.schemas?.ui || config.ui_schema || config.ui || {},
    api: config.schemas?.api || config.api_schema || config.api || {},
    db: config.schemas?.db || config.db_schema || config.db || {},
    auth: config.schemas?.auth || config.auth_schema || config.auth || {}
  };
}

function normalizeValidation(config, metrics) {
  const source = toArray(config.validation || metrics.validation || metrics.checks);
  return source.map(item => {
    if (typeof item === 'string') {
      return { type: 'pass', msg: item };
    }

    const type = (item.type || item.status || 'pass').toLowerCase();
    const msg = item.msg || item.message || item.description || JSON.stringify(item);
    return { type, msg };
  });
}

function normalizeAssumptions(config) {
  const source = toArray(config.assumptions || config.notes || config.inferences);
  return source.map(item => {
    if (typeof item === 'string') {
      return { label: 'Assumption', text: item };
    }

    return {
      label: item.label || item.title || 'Assumption',
      text: item.text || item.message || item.description || JSON.stringify(item)
    };
  });
}

function toArray(value) {
  if (Array.isArray(value)) return value;
  if (value == null) return [];
  if (typeof value === 'object') return Object.values(value);
  return [value];
}

function extractName(value) {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'object') return value.name || value.title || value.route || value.label || '';
  return String(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}