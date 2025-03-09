'use strict';
let currentValue = 0;

const formFile = document.querySelector('#file-upload');
const dropdown = document.querySelector('#dropdown');

console.log("I'm beyond confused");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-upload");

// Highlight drop zone when a file is dragged over it
dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
});

// Remove highlight when dragging leaves the drop zone
dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

// Handle file drop
dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");

    // Get dropped files
    const files = event.dataTransfer.files;

    // Create a DataTransfer object to sync with file input
    const dataTransfer = new DataTransfer();
    Array.from(files).forEach(file => dataTransfer.items.add(file));

    // Assign dropped files to the file input
    fileInput.files = dataTransfer.files;

    console.log("Dropped files:", fileInput.files);
});

// Allow clicking on the drop zone to open file picker
dropZone.addEventListener("click", () => {
    fileInput.click();
});

// Handle form submission
const formButton = document.getElementById("form-button");
formButton.addEventListener("click", async (e) => {
    e.preventDefault();

    const myFiles = fileInput.files;
    const formData = new FormData();

    Object.keys(myFiles).forEach(key => {
        formData.append(myFiles.item(key).name, myFiles.item(key));
    });

    const response = await fetch("http://localhost:3000/api/upload/", {
        method: "POST",
        body: formData
    });

    const jsonData = await response.json();
    console.log(jsonData);
});

