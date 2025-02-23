const express = require('express');
const { escape } = require('querystring');
const app = express();

app.use(express.json());

const port = 3000;
const currentPath = __dirname;

app.get('/', (req, res) => {
    res.send("Hello world. Holder page");
    res.status(200).end();
})

app.get('/upload', (req, res) => {
    res.sendFile(`${currentPath}/templates/index.html`);
})

app.get('/payment', (req, res) => {
    res.sendFile(`${currentPath}/templates/payment.html`);
})



// Main app
app.listen(port, (error) => {
    if(error) console.log(`Error while booting server: ${error}.`);
    else console.log(`Server is running on port ${port}.`);

})