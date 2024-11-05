// Get the modal
var modal = document.getElementById("uploadModal");

// Open the modal
function openModal() {
    modal.style.display = "block";
}

// Close the modal
function closeModal() {
    modal.style.display = "none";
}

// Close the modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
