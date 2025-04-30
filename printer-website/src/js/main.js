'use strict';
let currentValue = 0;

const formFile = document.querySelector('#file-upload');
const dropdown = document.querySelector('#dropdown');

console.log("I'm beyond confused");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-upload");

const formButton = document.getElementById("form-button");
formButton.addEventListener("click", async (e) => {
    e.preventDefault();

    const myFiles = fileInput.files;
    const formData = new FormData();

    const folderName = Date.now().toString();
    formData.append("folderName", folderName);
    // user unique identifier key
    // formData.append("userID", userID);
    Object.keys(myFiles).forEach(key => {
        formData.append(myFiles.item(key).name, myFiles.item(key));
    });

    console.log(formData, typeof formData);

    const response = await fetch("/api/upload/", {
        method: "POST",
        body: formData
    });
    
});

