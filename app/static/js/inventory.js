function openModal(product_content, productId) {

    // set transaction id to hidden input fields
    const hiddenInput = document.getElementById('product-id');
    const hiddenInput2 = document.getElementById('product-id-delete');

    if (hiddenInput) {
        hiddenInput.value = parseInt(productId);
        hiddenInput2.value = parseInt(productId);
    }

    // set product id display value
    const productIdDisplay = document.getElementById('product-id-display');

    if (productIdDisplay) {
        productIdDisplay.innerHTML = productId;
    }

    // set product status selection to current status
    const productStatus = document.getElementById('product-status');
    productStatus.value = product_content['status'];

    // set product container size selection to current size
    const productContainerSize = document.getElementById('product-container-size');
    productContainerSize.value = product_content['container_size'];

    // set modifiable product attribute inputs
    const productAttributes = Object.keys(product_content);

    // set flavor, price, and quantity inputs
    productAttributes.forEach(attribute => {
        const inputField = document.getElementById(`product-${attribute}`);

        if (inputField) {
            inputField.value = product_content[attribute];
        }
    });

    $('#productModal').modal('show'); // Show the modal

    console.log("Modal opened");
}

function closeModal() {
    $('#productModal').modal('hide'); // Hide the modal

    console.log("Modal closed");
}