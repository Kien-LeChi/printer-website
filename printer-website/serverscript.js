const express = require('express');
const { escape } = require('querystring');
const path = require('path');
const multer = require('multer');

const multerStorage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'usr/uploaded');
    },
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    },
})

const fileUpload = multer({
    storage: multerStorage,
    fileFilter: (req, file, cb) => {
        const validFileTypes = /png|pdf/;
        const extname = validFileTypes.test(path.extname(file.originalname).toLowerCase())

        if(extname === true) {
            // Return true and file is saved
             return cb(null, true)
        } else {
            // Return error message if file extension does not match
            return cb("Error: Images Only!")
        }
    },
})
const app = express();

app.use(express.json());
app.use('/static', express.static(path.join(__dirname, 'src')));

const port = 3001;

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates/index.html'));
})

app.post('/api/upload/', fileUpload.any('test'), (req, res) => {
    res.json(req.file);
})

app.get('/helloTuomas', (req, res) => {
    res.send("Hello Tuomas! Minulla on Tuomakseen kukko.")
})

// Main app
app.listen(port, (error) => {
    if(error) console.log(`Error while booting server: ${error}.`);
    else {
        console.log(`Server is running on port ${port}.`);
        console.log(__dirname);
    }
})