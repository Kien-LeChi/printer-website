const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require("fs-extra");
const chokidar = require('chokidar');

const app = express();

// Multer file storage and configuration
const baseDir = path.join(__dirname);
const uploadBaseDir = path.join(__dirname, 'files/uploaded');
const processedBaseDir = path.join(__dirname, 'files/processed');

[uploadBaseDir, processedBaseDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

const multerStorage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadFolder = path.join(uploadBaseDir, req.body.folderName || Date.now());

        if (!fs.existsSync(uploadFolder)) {
            fs.mkdirSync(uploadFolder, { recursive: true });
        }

        cb(null, uploadFolder);
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        const baseName = path.basename(file.originalname, ext);

        const newFileName = `${baseName}-${Date.now()}${ext}`;
        cb(null, newFileName);
    },
})

const fileUpload = multer({
    storage: multerStorage,
    fileFilter: (req, file, cb) => {
        const validFileTypes = /.docx|.pdf/;
        const extname = validFileTypes.test(path.extname(file.originalname).toLowerCase())

        if (extname === true) {
            return cb(null, true)
        } else {
            return cb("Error: PDF and Docx only!")
        }
    },
})


/* 
Simulated printer logic and directory watcher
*/

// Simulated printer logic
async function simulatePrintAndMove(folderPath, folderName) {
    console.log(`Processing folder: ${folderName}`);

    const files = await fs.promises.readdir(folderPath);
    
    for (const file of files) {
        const filePath = path.join(folderPath, file);
        console.log(`Printing file: ${filePath}`);
        // Simulate some processing delay (like printing)
        await new Promise(res => setTimeout(res, 1000));
    }

    // Move the folder to processed
    const destination = path.join(processedBaseDir, folderName);
    await fs.move(folderPath, destination, { overwrite: true });

    console.log(`Moved to processed: ${destination}`);
}

// Watcher
const folderWatcher = chokidar.watch(uploadBaseDir, {
    depth: 1,
    persistent: true,
    ignoreInitial: false,
    awaitWriteFinish: {
        stabilityThreshold: 2000,
        pollInterval: 100
    }
});

// Folder detection logic
folderWatcher.on('addDir', async (folderPath) => {
    if (folderPath === uploadBaseDir) return; // Ignore root watched dir

    const folderName = path.basename(folderPath);

    console.log(`New folder detected: ${folderName}`);

    
    setTimeout(async () => {
        try {
            await simulatePrintAndMove(folderPath, folderName);
        } catch (err) {
            console.error(`Error processing folder ${folderName}:`, err);
        }
    }, 3000);
});






/* API ROUTING */

app.post('/api/upload_files/', fileUpload.any('file-upload'), (req, res) => {
    console.log(req.body, typeof req.body);
    res.json(req.body);
})

// API status
app.get("/api/upload_files/", (req, res) => {
    res.send("The server is up");
    res.status(200).end();
})

// Main app
const port = 3001
app.listen(port, (error) => {
    console.log("Server running on port", port);
})