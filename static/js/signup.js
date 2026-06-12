// Toggle password visibility
document.querySelectorAll(".toggle-password").forEach(icon => {
  icon.addEventListener("click", () => {
    const input = document.getElementById(icon.getAttribute("data-target"));
    if (input.type === "password") {
      input.type = "text";
      icon.classList.replace("fa-eye", "fa-eye-slash");
    } else {
      input.type = "password";
      icon.classList.replace("fa-eye-slash", "fa-eye");
    }
  });
});

// Client-side password match check before submitting to Flask
document.querySelector("form").addEventListener("submit", (e) => {
  const pwd     = document.getElementById("password").value;
  const confirm = document.getElementById("confirmPassword").value;
  if (pwd !== confirm) {
    e.preventDefault();
    alert("Passwords do not match!");
  }
  // If they match, form submits normally to Flask
});
