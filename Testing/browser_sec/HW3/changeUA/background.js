chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    for (let i = 0; i < details.requestHeaders.length; i++) {
      if (details.requestHeaders[i].name.toLowerCase() === "user-agent") {
        const originalUA = details.requestHeaders[i].value;
        const modifiedUA = originalUA.replace(
          /Chrome\/[\d.]+/,
          'Chrome/14828'
        );
        details.requestHeaders[i].value = modifiedUA;
        break;
      }
    }
    return { requestHeaders: details.requestHeaders };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "requestHeaders"]
);