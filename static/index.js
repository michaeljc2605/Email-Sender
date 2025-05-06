const correctPassword = "ApplyForChina68";
const passwordInput = document.getElementById('password');
const correctNotification = document.getElementById('correct-notification');
const incorrectNotification = document.getElementById('incorrect-notification');
const fileSection = document.getElementById('file-section');

passwordInput.addEventListener('input', function() {
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

function checkPassword() {
    if (passwordInput.value !== correctPassword) {
        alert('Please enter the correct password before uploading.');
        return false;
    }
    return true;
}

// Make checkPassword available globally so the HTML form can call it
window.checkPassword = checkPassword;
