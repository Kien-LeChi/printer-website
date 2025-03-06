'use strict';
let currentValue = 0;

const formButton = document.querySelector('#form-button');

console.log("I'm beyond confused");
formButton.addEventListener('click', (e) => {
    e.preventDefault();
    const trackingNumber = document.querySelector('#test');
    currentValue++;
    trackingNumber.innerText = currentValue.toString();
})