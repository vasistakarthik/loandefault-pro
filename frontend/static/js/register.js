const password = document.getElementById("password");
const strengthBar = document.getElementById("strength-bar");
const confirmPassword = document.getElementById("confirmPassword");
const confirmError = document.getElementById("confirmError");

if (password && strengthBar) {
    password.addEventListener("input", function () {
        let val = password.value;
        let strength = 0;

        if (val.length > 6) strength += 25;
        if (/[A-Z]/.test(val)) strength += 25;
        if (/[0-9]/.test(val)) strength += 25;
        if (/[^A-Za-z0-9]/.test(val)) strength += 25;

        strengthBar.style.width = strength + "%";

        if (strength <= 25) strengthBar.style.background = "#ef4444";
        else if (strength <= 50) strengthBar.style.background = "#f59e0b";
        else if (strength <= 75) strengthBar.style.background = "#3b82f6";
        else strengthBar.style.background = "#22c55e";
    });
}

const registerForm = document.getElementById("registerForm");
if (registerForm && confirmPassword) {
    registerForm.addEventListener("submit", function (e) {
        if (password.value !== confirmPassword.value) {
            e.preventDefault();
            if (confirmError) {
                confirmError.innerText = "Passwords do not match!";
            } else {
                alert("Passwords do not match!");
            }
        } else if (confirmError) {
            confirmError.innerText = "";
        }
    });

    confirmPassword.addEventListener("input", function () {
        if (password.value !== confirmPassword.value && confirmPassword.value.length > 0) {
            if (confirmError) confirmError.innerText = "Passwords do not match!";
        } else {
            if (confirmError) confirmError.innerText = "";
        }
    });
}
