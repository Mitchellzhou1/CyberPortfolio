$(document).ready(function () {
    function replaceText(matchText, replaceText) {
        if (!matchText) return;

        $('*').contents().each(function () {
            if (this.nodeType === 3) {
                this.nodeValue = this.nodeValue.replace(new RegExp(matchText, 'g'), replaceText);
            }
        });
    }

    chrome.runtime.onMessage.addListener((request) => {
        replaceText(request.matchText, request.replaceText);
    });
});
