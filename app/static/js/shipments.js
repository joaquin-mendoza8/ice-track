// dom event listener for the shipment form
document.addEventListener('DOMContentLoaded', function() {

    // open the shipment update modal if the shipment id is in the url
    const urlParams = new URLSearchParams(window.location.search);
    const order_id = urlParams.get('order_id');
    if (order_id) {
        console.log('order_id:', order_id);
        document.getElementById(`order-${order_id}`).click();
    }

    // add event listener to toggle the edit mode
    $('#shipmentUpdateModal').on('hidden.bs.modal', function (event) {
        // check if the modal was closed by clicking the close button
        const orderUpdateModal = document.getElementById('ordersUpdateModal');
        if (event.target === orderUpdateModal) {
            toggleEdit(false);
        }

    });

});


function openShipmentUpdateModal(shipment_id) {

    // update the order details navigation button
    const navOrderBtn = document.getElementById('nav-order-btn');
    navOrderBtn.href = `/orders?shipment_id=${shipment_id}`;

    // clear the url params
    window.history.replaceState({}, document.title, "/shipments");

    // set the shipment id in the hidden input field
    $('#shipment-id-update').val(shipment_id);
    $('#shipment-id-update-hidden').val(shipment_id);

    // set any fields that contain form-control to form-control-plaintext
    $('input.form-control').each(function() {
        $(this).removeClass('form-control');
        $(this).addClass('form-control-plaintext');
    });

    // reset form-control class when the modal is closed
    $('#shipmentUpdateModal').on('hidden.bs.modal', function () {
        $('input.form-control-plaintext').each(function() {
            $(this).removeClass('form-control-plaintext');
            $(this).addClass('form-control');
        });
    });

    // fetch the shipment details from the server
    fetch(`/fetch_shipment_info?shipment_id=${shipment_id}`)
        .then(response => response.json())
        .then(data => {

            const shipmentContent = data;

            console.log('shipmentContent:', shipmentContent);

            // check if there is an error
            if ('error' in shipmentContent) {
                alert(`Failed to load shipment info. ${shipmentContent.error}. Please contact support.`);
                return;
            }

            // dynamically set the shipment details in the form
            Object.keys(shipmentContent).forEach(key => {
                const fieldId = `#${key.replace(/_/g, '-')}-update`;

                console.log('fieldId:', fieldId, 'value:', shipmentContent[key]);

                // check if the field exists
                if ($(fieldId).length) {

                    // check if the field is a string and not the order status
                    if (/^[a-zA-Z]+$/.test(shipmentContent[key]) && key !== 'order_status') {
                        const content = shipmentContent[key];

                        // capitalize the first letter of the string
                        if (typeof content === 'string') {
                            const capitalizedContent = content.charAt(0).toUpperCase() + content.slice(1);
                            $(fieldId).val(capitalizedContent);
                        } else {
                            $(fieldId).val(content);
                        }
                    } else {

                        // set the value of the field
                        $(fieldId).val(shipmentContent[key]);
                        // console.log('fieldId:', fieldId, 'value:', shipmentContent[key]);
                    }
                }
            });
        });

    // open modal
    $('#shipmentUpdateModal').modal('show');
}


function toggleEdit(toEditMode) {

    // get the order status
    const orderStatusSelect = document.getElementById('order-status-update');
    const orderStatus = orderStatusSelect.options[orderStatusSelect.selectedIndex].value;

    // get the update button
    const updateButton = document.getElementById('updateShipmentButton');

    // if the update button is disabled and the toEditMode is false, don't toggle the edit mode
    if (!toEditMode && updateButton.disabled) {
        return;
    }

    // toggle the update button to show/hide
    updateButton.disabled = !updateButton.disabled;

    // get all input fields in the modal
    const updateModal = document.getElementById('shipmentUpdateModal');
    const updateInputs = updateModal.querySelectorAll('[id*="-update"]');
    let inputsFixedReadOnly = [
        'order-status-update',
        'shipment-id-update',
        'order-id-update',
        'shipment-id-update-hidden',
        'shipment-type-update',
        'estimated-delivery-date-update',
        'partial-delivery-date-update',
        'shipment-boxes-update',
        'partial-delivery-update',
        'date-shipped-update',
    ]

    // toggle the disabled attribute for select elements and the readonly attribute for input elements
    updateInputs.forEach(input => {

        // don't allow editing of desired receipt date if order is cancelled
        if (orderStatus === 'cancelled' && 
            (input.id === 'desired-receipt-date-update' || input.id === 'order-status-update')) {
            return;
        }

        // toggle disabled attribute for select elements
        if (!inputsFixedReadOnly.includes(input.id)) {
            if (input.tagName === 'SELECT') {
                input.disabled = !input.disabled;
            } else if (input.classList.contains('form-control-plaintext')) {
                input.classList.remove('form-control-plaintext');
                input.classList.add('form-control');
                input.readOnly = !input.readOnly;
            } else {
                input.classList.remove('form-control');
                input.classList.add('form-control-plaintext');
                input.readOnly = !input.readOnly;
            }
        }

    });

}