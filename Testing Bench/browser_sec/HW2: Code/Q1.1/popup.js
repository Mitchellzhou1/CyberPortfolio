document.addEventListener("DOMContentLoaded", function () {
    const nameInput = document.getElementById("nameInput");
    const greeting = document.getElementById("greeting");

    nameInput.addEventListener("input", function () {
        const name = nameInput.value.trim();
        greeting.textContent = name ? `Hello ${name}!` : "";
    });
});
