const express = require('express');
const path = require('path')
const xml = require('xml')

const app = express()
const port = 3005

app.get('/', (req, res) => {
    res.send("App is running");
})

app.get('/file', (req, res) => {
    res.sendFile(path.join(__dirname, "./pdf.pdf/"));
})

app.get('/xml', (req, res) => {
    res.type("application/xml");
    res.sendFile(path.join(__dirname, "/test.xml"));
})

app.post('/xml', (req, res) => {
    res.type("application/xml");
    res.sendFile(path.join(__dirname, "/test.xml"));
})

app.listen(port, (err) => {
    console.log("App running on port", port);
})