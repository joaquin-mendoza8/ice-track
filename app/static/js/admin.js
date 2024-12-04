document.addEventListener('DOMContentLoaded', function() {

    // select the delete modal
    var deleteModal = document.getElementById('deleteModal');

    // event listener for when the modal is about to be shown
    deleteModal.addEventListener('show.bs.modal', function(event) {
        // button that triggered the modal
        var button = event.relatedTarget;

        // extract info from data-config-id attribute
        var configId = button.getAttribute('data-config-id');

        // update the hidden input and the confirm-delete button
        var hiddenInput = deleteModal.querySelector('#config-id-delete');

        if (hiddenInput) {
            hiddenInput.value = parseInt(configId);
        }
    });
});