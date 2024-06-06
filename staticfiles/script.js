$(document).ready(function() {
    // Hide Django messages after 5 seconds (5000 milliseconds)
    setTimeout(function() {
        $(".message").fadeOut('slow');
    }, 3000); // Adjust time as needed
});
