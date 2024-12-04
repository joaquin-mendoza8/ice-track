document.addEventListener('DOMContentLoaded', function() {

    // Enable Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // set a timeout to remove the alert messages after a certain time (default is 10 seconds)
    let timeout = 10;
    setTimeout(function() {
        var alertElement = document.querySelector('.alert');
        if (alertElement) {
            const alertTimeout = alertElement.getAttribute('data-timeout');
            if (alertTimeout) {
                timeout = parseInt(alertTimeout);
            }
        }
        if (alertElement) {
            alertElement.remove();
            // Remove URL request args
            const url = new URL(window.location);
            url.searchParams.delete('msg');
            url.searchParams.delete('msg_type');
            window.history.replaceState({}, document.title, url.toString());
        }
    }, timeout * 1000);
});