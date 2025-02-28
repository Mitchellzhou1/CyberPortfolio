document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("replaceBtn").addEventListener("click", function () {
        const matchText = document.getElementById("matchText").value;
        const replaceText = document.getElementById("replaceText").value;

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { matchText, replaceText });
        });
    });
});
