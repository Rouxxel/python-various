/**
 * Popup template – click counter (persisted) and optional backend ping.
 * Set BACKEND_BASE_URL below or in storage (key: backendBaseUrl) to enable the "Ping backend" section.
 */

(function () {
  // Leave empty to hide backend section. Example: 'http://localhost:8000'
  const BACKEND_BASE_URL = '';

  const els = {
    count: document.getElementById('count'),
    countBtn: document.getElementById('countBtn'),
    backendSection: document.getElementById('backendSection'),
    pingBtn: document.getElementById('pingBtn'),
    pingStatus: document.getElementById('pingStatus'),
  };

  const STORAGE_KEY_COUNT = 'clickCount';
  const STORAGE_KEY_BACKEND = 'backendBaseUrl';

  function showBackendSectionIfConfigured() {
    chrome.storage.local.get([STORAGE_KEY_BACKEND], function (data) {
      const base = data[STORAGE_KEY_BACKEND] || BACKEND_BASE_URL;
      if (base && typeof base === 'string' && base.trim() !== '') {
        els.backendSection.hidden = false;
      }
    });
  }

  function loadCount() {
    chrome.storage.local.get([STORAGE_KEY_COUNT], function (data) {
      const n = typeof data[STORAGE_KEY_COUNT] === 'number' ? data[STORAGE_KEY_COUNT] : 0;
      els.count.textContent = n;
    });
  }

  function incrementCount() {
    chrome.storage.local.get([STORAGE_KEY_COUNT], function (data) {
      const next = (typeof data[STORAGE_KEY_COUNT] === 'number' ? data[STORAGE_KEY_COUNT] : 0) + 1;
      chrome.storage.local.set({ [STORAGE_KEY_COUNT]: next }, function () {
        els.count.textContent = next;
      });
    });
  }

  function setPingStatus(text, isError) {
    els.pingStatus.textContent = text;
    els.pingStatus.className = 'ping-status' + (isError ? ' error' : text ? ' success' : '');
  }

  function getBackendBase() {
    return new Promise(function (resolve) {
      chrome.storage.local.get([STORAGE_KEY_BACKEND], function (data) {
        const base = (data[STORAGE_KEY_BACKEND] || BACKEND_BASE_URL || '').trim().replace(/\/$/, '');
        resolve(base);
      });
    });
  }

  async function pingBackend() {
    const base = await getBackendBase();
    if (!base) {
      setPingStatus('Set backendBaseUrl in storage or BACKEND_BASE_URL in code.', true);
      return;
    }
    setPingStatus('Pinging…');
    try {
      const url = base + '/health';
      const res = await fetch(url, { method: 'GET' });
      if (res.ok) {
        const text = await res.text();
        setPingStatus('OK: ' + (text || res.status));
      } else {
        setPingStatus('Error: ' + res.status, true);
      }
    } catch (e) {
      setPingStatus(e.message || 'Request failed', true);
    }
  }

  loadCount();
  showBackendSectionIfConfigured();

  els.countBtn.addEventListener('click', incrementCount);
  els.pingBtn.addEventListener('click', pingBackend);
})();
