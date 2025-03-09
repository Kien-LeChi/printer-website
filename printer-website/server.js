const express = require('express');
const { escape } = require('querystring');
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const chokidar = require('chokidar');

const app = express();

const uploadBaseDir = path.join(__dirname, 'usr/uploaded');
const processedBaseDir = path.join(__dirname, 'usr/processed');

[uploadBaseDir, processedBaseDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

const multerStorage = multer.diskStorage({
    destination: (req, file, cb) => {
        req.uploadTimestamp = Date.now();
        req.uploadFolder = path.join(uploadBaseDir, `upload-${req.uploadTimestamp}`);

        if (!fs.existsSync(req.uploadFolder)) {
            fs.mkdirSync(req.uploadFolder, { recursive: true });
        }

        cb(null, req.uploadFolder);
    },
    filename: (req, file, cb) => {
        const timeStamp = Date.now();
        const ext = path.extname(file.originalname);
        const baseName = path.basename(file.originalname, ext);

        const newFileName = `${baseName}-${timeStamp}${ext}`;
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

chokidar.watch(uploadBaseDir, { persistent: true, depth: 1 }).on('addDir', (folderPath) => {
    console.log(`New upload folder detected: ${folderPath}`);

    // Call for print function goes here.

    const folderName = path.basename(folderPath);
    const newFolderPath = path.join(processedBaseDir, folderName);

    // Move the entire folder to processed directory
    fs.rename(folderPath, newFolderPath, (err) => {
        if (err) {
            console.error(`Error moving folder: ${err}`);
        } else {
            console.log(`Folder moved to ${newFolderPath}`);
        }
    });
});

app.use(express.json());
app.use('/static', express.static(path.join(__dirname, 'src')));

const port = 3000;


/* WEB-SERVER ROUTING */
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates/index.html'));
})





/* ALL API ROUTES */
app.post('/api/upload/', fileUpload.any('test'), (req, res) => {
    res.json(req.files);
    res.status(203).end();
})



// Main app
app.listen(port, (error) => {
    if (error) console.log(`Error while booting server: ${error}.`);
    else {
        console.log(`Server is running on port ${port}.`);
        console.log(__dirname);
    }
})