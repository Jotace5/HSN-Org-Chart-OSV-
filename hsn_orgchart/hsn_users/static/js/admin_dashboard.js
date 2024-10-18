document.addEventListener("DOMContentLoaded", function() {
    const messages = document.getElementsByClassName('message');
    
    for (let i = 0; i < messages.length; i++) {
        let messageText = messages[i].innerText;

        if (messageText.includes('Data extraction process started')) {
            // Show the loading spinner
            document.getElementById('loading-spinner').style.display = 'block';
        }

        if (messageText.includes('Data extraction completed successfully') || messageText.includes('Failed')) {
            // Hide the loading spinner
            document.getElementById('loading-spinner').style.display = 'none';
        }
    }
});
 
 
 // Get the modal
 var modal = document.getElementById("fileUploadModal");
 // Get the button that opens the modal
 var btn = document.getElementById("loadDatabaseButton");
 // Get the <span> element that closes the modal
 var span = document.getElementById("closeModal");

 // When the user clicks the button, open the modal 
 btn.onclick = function() {
     modal.style.display = "block";
 }

 // When the user clicks on <span> (x), close the modal
 span.onclick = function() {
     modal.style.display = "none";
 }

 // When the user clicks anywhere outside of the modal, close it
 window.onclick = function(event) {
     if (event.target == modal) {
         modal.style.display = "none";
     }
 }

 // Your existing D3.js code to render the organizational chart
 d3.json(chartDataUrl).then(function (data) {
    console.log(data); // Replace this with your D3.js code to visualize the data
}).catch(function (error) {
    console.error('Error loading data:', error);
});