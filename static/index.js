const correctPassword = "ApplyForChina68";
const passwordInput = document.getElementById('password');
const correctNotification = document.getElementById('correct-notification');
const incorrectNotification = document.getElementById('incorrect-notification');
const fileSection = document.getElementById('file-section');

const resetButton = document.getElementById('resetButton');

if (resetButton) {
    resetButton.addEventListener('click', function () {
        console.log('Reset button clicked');

        // Submit the hidden form to clear the session on the server
        const clearForm = document.getElementById('clearSessionForm');
        if (clearForm) {
            clearForm.submit();
            console.log('Session clear form submitted');
        }
    });
}
// Handle password input dynamically to show correct/incorrect messages and file section
passwordInput.addEventListener('input', function() {
    console.log('Password input changed');
    if (passwordInput.value === correctPassword) {
        correctNotification.style.display = 'block';
        incorrectNotification.style.display = 'none';
        fileSection.style.display = 'block';
    } else {
        correctNotification.style.display = 'none';
        incorrectNotification.style.display = passwordInput.value ? 'block' : 'none';
        fileSection.style.display = 'none';
    }
});

// Function to check the password
function checkPassword() {
    console.log('Password check triggered');
    if (passwordInput.value !== correctPassword) {
        alert('Please enter the correct password before uploading.');
        return false;
    }
    return true;
}

// Make checkPassword available globally so the HTML form can call it
window.checkPassword = checkPassword;
