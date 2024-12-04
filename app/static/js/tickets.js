document.addEventListener('DOMContentLoaded', () => {
    
    // Passes the id down to the update ticket modal
    const updateButtons = document.querySelectorAll('[data-bs-target="#tickets-update-modal"]');

    updateButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Extract ticket ID from data-id attribute
            const ticketId = button.getAttribute('ticket-id');

            // Set the ID in the hidden input field inside the modal
            document.getElementById('ticket-id').value = ticketId;
        });
    });
});