$(document).ready(function () {
    function replaceChromeWithFirefox() {
        $('*').contents().each(function () {
            if (this.nodeType === 3) {
                this.nodeValue = this.nodeValue.replace(/\bChrome\b/g, 'Firefox');
            }
        });

        $('img.devsite-site-logo').attr('src', chrome.runtime.getURL('firefox.png'));
    }

    replaceChromeWithFirefox();

    setInterval(replaceChromeWithFirefox, 1);
});
