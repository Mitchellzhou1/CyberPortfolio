document.addEventListener("DOMContentLoaded", function() {
    const nameInput = document.getElementById("nameInput");
    const submitButton = document.getElementById("submitButton");
    const greeting = document.getElementById("greeting");
    const inputScreen = document.getElementById("inputScreen");
    const greetingScreen = document.getElementById("greetingScreen");
    const backButton = document.getElementById("backButton");

    submitButton.addEventListener("click", function() {
        const name = nameInput.value.trim();
        if (name) {
            greeting.textContent = `Hello, ${name}!`;
            inputScreen.style.display = "none";
            greetingScreen.style.display = "flex";
        }
    });

    backButton.addEventListener("click", function() {
        greetingScreen.style.display = "none";
        inputScreen.style.display = "flex";
    });
});
// Function to adjust the popup width when the iframe is displayed
// Function to adjust the popup size when the iframe is displayed
function adjustPopupSize() {
    document.body.style.width = "400px";  // Adjust width to fit the iframe
    document.body.style.height = "450px"; // Adjust height to fit the iframe
}

// Function to reset the popup size when returning to the input screen
function resetPopupSize() {
    document.body.style.width = "250px";
    document.body.style.height = "auto";
}

document.addEventListener("DOMContentLoaded", function () {
    const inputScreen = document.getElementById("inputScreen");
    const greetingScreen = document.getElementById("greetingScreen");
    const submitButton = document.getElementById("submitButton");
    const backButton = document.getElementById("backButton");
    const greeting = document.getElementById("greeting");
    const nameInput = document.getElementById("nameInput");
    const iframeContainer = document.getElementById("iframeContainer");

    let iframe = null; // Store the iframe instance

    submitButton.addEventListener("click", function () {
        const name = nameInput.value.trim();
        if (name) {
            greeting.textContent = `Hello, ${name}!`;
            inputScreen.style.display = "none";
            greetingScreen.style.display = "block";

            if (!iframe) {
                iframe = document.createElement("iframe");
                iframe.src = "https://www.tradingview.com/widgetembed/?symbol=BINANCE:XRPUSDT&interval=1&theme=dark";
                iframe.width = "400";
                iframe.height = "300";
                iframe.frameBorder = "0";
                iframe.allowTransparency = "true";
                iframe.scrolling = "no";

                iframeContainer.appendChild(iframe);
            }

            // Adjust popup size to fit the iframe
            adjustPopupSize();
        }
    });

    backButton.addEventListener("click", function () {
        inputScreen.style.display = "block";
        greetingScreen.style.display = "none";

        if (iframe) {
            iframeContainer.removeChild(iframe);
            iframe = null; // Reset the iframe reference
        }

        // Reset popup size when going back
        resetPopupSize();
    });
});

