
(function applySettings() {
  const get = (key, def) => {
    const v = localStorage.getItem(key);
    if (v === null) return def;
    if (v === 'true') return true;
    if (v === 'false') return false;
    const n = Number(v);
    return isNaN(n) ? v : n;
  };

  function apply() {
    const body = document.body;
    if (!body) return;  // safety check

    if (get('sg_darkMode',      false)) body.classList.add('dark-mode');
    if (get('sg_highContrast',  false)) body.classList.add('high-contrast');
    if (get('sg_largeButtons',  false)) body.classList.add('large-buttons');
    if (get('sg_reducedMotion', false)) body.classList.add('reduced-motion');

    const fs = get('sg_fontSize', 16);
    document.documentElement.style.fontSize = fs + 'px';
  }

  // Run immediately if body exists, otherwise wait for DOM
  if (document.body) {
    apply();
  } else {
    document.addEventListener('DOMContentLoaded', apply);
  }
})();

// Global TTS helpers — used by live_translation & history pages
window.SGSettings = {
  isAudioOn:     () => localStorage.getItem('sg_audioOutput') !== 'false',
  getVolume:     () => Number(localStorage.getItem('sg_volume') ?? 75) / 100,
  getSpeechRate: () => localStorage.getItem('sg_speechRate') || 'normal',
};