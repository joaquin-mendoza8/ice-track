function openModal(product_content, productId) {

    // set transaction id to hidden input field
    const hiddenInput = document.getElementById('product-id');

    if (hiddenInput) {
        hiddenInput.value = parseInt(productId);
    }
    // const transactionNameInput = document.getElementById('product_flavor');

    // set product id display value
    const productIdDisplay = document.getElementById('product-id-display');

    if (productIdDisplay) {
        productIdDisplay.innerHTML = productId;
    }

    // set modifiable product attribute inputs
    const productAttributes = Object.keys(product_content);

    // set flavor, price, and quantity inputs
    productAttributes.forEach(attribute => {
        const inputField = document.getElementById(`product-${attribute}`);

        if (inputField.id === 'product-id') {
            inputField.value = parseInt(productId);
        } else if (inputField) {
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

