const express = require('express');
const { escape } = require('querystring');
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const chokidar = require('chokidar');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();

app.use(express.json());
app.use('/static', express.static(path.join(__dirname, 'src')));
app.use(bodyParser.json());

const baseDir = path.join(__dirname);
const uploadBaseDir = path.join(__dirname, 'usr/uploaded');
const processedBaseDir = path.join(__dirname, 'usr/processed');

[uploadBaseDir, processedBaseDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

const multerStorage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadFolder = path.join(uploadBaseDir, req.body.folderName || Date.now().toString());

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


/* WEB-SERVER ROUTING */
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates/index.html'));
})

app.get('/printer_homepage/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates/printer.html'));
})

app.get('/payment', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates/payment.html'))
})

/* ALL API ROUTES */
app.post('/api/upload/', fileUpload.any('file-upload'), async (req, res) => {

    console.log(req.body, typeof req.body);

    const formData = new FormData();
    const formObject = req.body;

    for (let key in formObject) {
        formData.append(key, formObject[key]);
    }

    // const response = await fetch('/api/upload_files/', {
    //     method: "POST",
    //     body: formData
    // });
    res.sendStatus(200).end();
})

//      Get latest file uploaded
app.get('/api/uploads/get', (req, res) => {

})


// Main app
const port = 3000;
app.listen(port, "0.0.0.0", (error) => {
    if (error) console.log(`Error while booting server: ${error}.`);
    else {
        console.log(`Server is running on port ${port}.`);
        console.log(__dirname);
    }
})