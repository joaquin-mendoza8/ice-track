function openModal(order_content, orderId) {

    // set transaction id to hidden input fields
    // const hiddenInput = document.getElementById('product-id');
    // const hiddenInput2 = document.getElementById('product-id-delete');

    // if (hiddenInput) {
    //     hiddenInput.value = parseInt(productId);
    //     hiddenInput2.value = parseInt(productId);
    // }

    // // set product id display value
    // const productIdDisplay = document.getElementById('product-id-display');

    // if (productIdDisplay) {
    //     productIdDisplay.innerHTML = productId;
    // }

    // // set modifiable product attribute inputs
    // const productAttributes = Object.keys(product_content);

    // // set flavor, price, and quantity inputs
    // productAttributes.forEach(attribute => {
    //     const inputField = document.getElementById(`product-${attribute}`);

    //     if (inputField.id === 'product-id') {
    //         inputField.value = parseInt(productId);
    //     } else if (inputField) {
    //         inputField.value = product_content[attribute];
    //     }
    // });

    $('#productModal').modal('show'); // Show the modal

    console.log("Modal opened");
}

function closeModal() {
    $('#productModal').modal('hide'); // Hide the modal

    console.log("Modal closed");
}

document.addEventListener('DOMContentLoaded', function() {
    const flavorSelect = document.getElementById('flavor');
    const sizeSelect = document.getElementById('size');

    flavorSelect.addEventListener('change', function() {
        // get the inner text of the selected option
        const selectedFlavor = flavorSelect.options[flavorSelect.selectedIndex].text;
        console.log("Selected Flavor: ", selectedFlavor);

        // Clear the Size dropdown
        sizeSelect.innerHTML = '<option value="">Select a size</option>';

        if (selectedFlavor) {
            fetch(`/orders/get_sizes?flavor=${encodeURIComponent(selectedFlavor)}`)
                .then(response => response.json())
                .then(data => {
                    console.log("RETRIEVED DATA: ", data);
                    data.sizes.forEach(size => {
                        const option = document.createElement('option');
                        option.value = size;
                        option.textContent = size;
                        sizeSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching sizes:', error);
                    alert('Failed to load sizes. Please try again.');
                });
        }
    });
});