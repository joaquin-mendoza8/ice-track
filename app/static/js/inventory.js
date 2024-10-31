// DOM content loaded event listener
document.addEventListener('DOMContentLoaded', function() {

    // set product price, quantity, and status inputs to current values when dropdowns are changed
    const flavorSelect = document.getElementById('product-flavor-add');
    const sizeSelect = document.getElementById('product-container-size-add');

    // set event listeners for flavor and container size dropdowns
    flavorSelect.addEventListener('change', updateModalInputs);
    sizeSelect.addEventListener('change', updateModalInputs);

    // set event listener for status dropdown
    const statusSelect = document.getElementById('product-status-add');
    statusSelect.addEventListener('change', updateDockDropdown);

    // TODO: finish dock date js

});


// Function to update product price and quantity inputs based on flavor and container size dropdowns
function updateModalInputs() {

    // get flavor and container size dropdown values
    const flavorSelect = document.getElementById('product-flavor-add');
    const sizeSelect = document.getElementById('product-container-size-add');

    // get product price and quantity inputs
    const priceInput = document.getElementById('product-price-add');
    const quantityInput = document.getElementById('product-quantity-add');

    const selectedFlavor = flavorSelect.value;
    const selectedSize = sizeSelect.value;

    if (selectedFlavor && selectedSize && (sizeSelect.value !== 'Select size')) {
        
        // fetch stock of selected product
        fetch(`/orders/fetch_stock?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
            .then(response => response.json())
            .then(data => {

                quantityInput.value = data.stock;

            })
            .catch(error => {
                console.error('Error fetching stock:', error);
                alert('Failed to load stock. Please try again.');
            });
        
        // fetch price of selected product
        fetch(`/orders/fetch_cost?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}&quantity=1`)
            .then(response => response.json())
            .then(data => {

                if (data.cost != 0.0) {
                    priceInput.value = data.cost.toFixed(2);
                }

            })
            .catch(error => {
                console.error('Error fetching price:', error);
                alert('Failed to load price. Please try again.');
            });

        // fetch status of selected product
        fetch(`/orders/fetch_product_status?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
            .then(response => response.json())
            .then(data => {

                if (data.status) {
                    const statusInput = document.getElementById('product-status-add');
                    statusInput.value = data.status;
                }


            })
            .catch(error => {
                console.error('Error fetching status:', error);
                alert('Failed to load status. Please try again.');
            });
    }
}


function openModal(product_content, productId, isAdmin) {

    // don't allow editing of product if not admin
    if (!isAdmin) {
        return;
    }

    console.log(product_content);

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
}

function closeModal() {
    $('#productModal').modal('hide'); // Hide the modal
}