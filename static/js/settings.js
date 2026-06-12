const KEYS = {
  darkMode: "sg_darkMode",
  fontSize: "sg_fontSize",
  highContrast: "sg_highContrast",
  reducedMotion: "sg_reducedMotion",
  pushNotif: "sg_pushNotif",
  emailNotif: "sg_emailNotif",
  dataCollect: "sg_dataCollect",
  autoSave: "sg_autoSave",
  offlineMode: "sg_offlineMode",
  autoOptimize: "sg_autoOptimize",
  qualityMode: "sg_qualityMode",
};

const DEFAULTS = {
  darkMode: false,
  fontSize: 16,
  highContrast: false,
  reducedMotion: false,
  pushNotif: true,
  emailNotif: true,
  dataCollect: true,
  autoSave: true,
  offlineMode: false,
  autoOptimize: true,
  qualityMode: "Balanced",
};

function loadSetting(key) {
  const value = localStorage.getItem(KEYS[key]);

  if (value === null) return DEFAULTS[key];
  if (value === "true") return true;
  if (value === "false") return false;

  const num = Number(value);
  return isNaN(num) ? value : num;
}

function saveSetting(key, value) {
  localStorage.setItem(KEYS[key], value);
}

function applyTheme() {
  const darkMode = loadSetting("darkMode");
  const highContrast = loadSetting("highContrast");
  const reducedMotion = loadSetting("reducedMotion");
  const fontSize = loadSetting("fontSize");

  document.body.classList.toggle("dark-mode", darkMode);
  document.body.classList.toggle("high-contrast", highContrast);
  document.body.classList.toggle("reduced-motion", reducedMotion);
  document.documentElement.style.fontSize = fontSize + "px";
}

function applyUIValues() {
  const darkModeEl = document.getElementById("darkMode");
  const fontSizeSliderEl = document.getElementById("fontSizeSlider");
  const fontSizeValueEl = document.getElementById("fontSizeValue");
  const highContrastEl = document.getElementById("highContrast");
  const reducedMotionEl = document.getElementById("reducedMotion");
  const pushNotifEl = document.getElementById("pushNotif");
  const emailNotifEl = document.getElementById("emailNotif");
  const dataCollectEl = document.getElementById("dataCollect");
  const autoSaveEl = document.getElementById("autoSave");
  const offlineModeEl = document.getElementById("offlineMode");
  const autoOptimizeEl = document.getElementById("autoOptimize");
  const qualityModeEl = document.getElementById("qualityMode");

  const fontSize = loadSetting("fontSize");

  if (darkModeEl) darkModeEl.checked = loadSetting("darkMode");
  if (fontSizeSliderEl) fontSizeSliderEl.value = fontSize;
  if (fontSizeValueEl) fontSizeValueEl.textContent = fontSize + "px";
  if (highContrastEl) highContrastEl.checked = loadSetting("highContrast");
  if (reducedMotionEl) reducedMotionEl.checked = loadSetting("reducedMotion");
  if (pushNotifEl) pushNotifEl.checked = loadSetting("pushNotif");
  if (emailNotifEl) emailNotifEl.checked = loadSetting("emailNotif");
  if (dataCollectEl) dataCollectEl.checked = loadSetting("dataCollect");
  if (autoSaveEl) autoSaveEl.checked = loadSetting("autoSave");
  if (offlineModeEl) offlineModeEl.checked = loadSetting("offlineMode");
  if (autoOptimizeEl) autoOptimizeEl.checked = loadSetting("autoOptimize");
  if (qualityModeEl) qualityModeEl.value = loadSetting("qualityMode");
}

function applyAll() {
  applyTheme();
  applyUIValues();
}

function saveAll() {
  saveSetting("darkMode", document.getElementById("darkMode").checked);
  saveSetting("fontSize", document.getElementById("fontSizeSlider").value);
  saveSetting("highContrast", document.getElementById("highContrast").checked);
  saveSetting("reducedMotion", document.getElementById("reducedMotion").checked);
  saveSetting("pushNotif", document.getElementById("pushNotif").checked);
  saveSetting("emailNotif", document.getElementById("emailNotif").checked);
  saveSetting("dataCollect", document.getElementById("dataCollect").checked);
  saveSetting("autoSave", document.getElementById("autoSave").checked);
  saveSetting("offlineMode", document.getElementById("offlineMode").checked);
  saveSetting("autoOptimize", document.getElementById("autoOptimize").checked);
  saveSetting("qualityMode", document.getElementById("qualityMode").value);

  applyAll();
  showToast("✅ Settings saved successfully!");
}

function resetAll() {
  Object.values(KEYS).forEach((key) => localStorage.removeItem(key));
  applyAll();
  showToast("↩️ Settings reset to default!");
}

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 2500);
}

document.addEventListener("DOMContentLoaded", () => {
  applyAll();

  const darkModeEl = document.getElementById("darkMode");
  const fontSizeSliderEl = document.getElementById("fontSizeSlider");
  const fontSizeValueEl = document.getElementById("fontSizeValue");
  const highContrastEl = document.getElementById("highContrast");
  const reducedMotionEl = document.getElementById("reducedMotion");
  const saveBtnEl = document.getElementById("saveBtn");
  const resetBtnEl = document.getElementById("resetBtn");

  if (darkModeEl) {
    darkModeEl.addEventListener("change", function () {
      document.body.classList.toggle("dark-mode", this.checked);
    });
  }

  if (highContrastEl) {
    highContrastEl.addEventListener("change", function () {
      document.body.classList.toggle("high-contrast", this.checked);
    });
  }

  if (reducedMotionEl) {
    reducedMotionEl.addEventListener("change", function () {
      document.body.classList.toggle("reduced-motion", this.checked);
    });
  }

  if (fontSizeSliderEl && fontSizeValueEl) {
    fontSizeSliderEl.addEventListener("input", function () {
      fontSizeValueEl.textContent = this.value + "px";
      document.documentElement.style.fontSize = this.value + "px";
    });
  }

  if (saveBtnEl) {
    saveBtnEl.addEventListener("click", saveAll);
  }

  if (resetBtnEl) {
    resetBtnEl.addEventListener("click", resetAll);
  }
});

/* Optional: use on other pages */
window.SGSettings = {
  applyGlobal: function () {
    const darkMode = localStorage.getItem("sg_darkMode") === "true";
    const highContrast = localStorage.getItem("sg_highContrast") === "true";
    const reducedMotion = localStorage.getItem("sg_reducedMotion") === "true";
    const fontSize = localStorage.getItem("sg_fontSize") || 16;

    document.body.classList.toggle("dark-mode", darkMode);
    document.body.classList.toggle("high-contrast", highContrast);
    document.body.classList.toggle("reduced-motion", reducedMotion);
    document.documentElement.style.fontSize = fontSize + "px";
  }
};