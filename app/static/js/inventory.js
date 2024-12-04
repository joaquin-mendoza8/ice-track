// DOM content loaded event listener
document.addEventListener('DOMContentLoaded', function() {

    // get all "disposition-" elements
    const dispositionElements = document.querySelectorAll('[id^="disposition-"]');

    // disable "shipped" option in disposition dropdowns
    const dispositionOptions = document.querySelectorAll('[id^="disposition-"] option');
    dispositionOptions.forEach(option => {
        if (option.value === 'shipped') {
            option.disabled = true;
        }
    });

    // attach event listener to navigate to disposition page when select is changed
    dispositionElements.forEach(element => {
        element.addEventListener('change', function() {
            const allocationId = element.id.split('-')[1];
            const dispositionValue = element.value;

            // fetch disposition update
            fetch(`/inventory_update_allocation?id=${allocationId}&disposition=${encodeURIComponent(dispositionValue)}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Disposition updated:', data);

                    // reload page and move back to element
                    location.reload();
                })
                .catch(error => {
                    console.error('Error updating disposition:', error);
                    alert('Failed to update disposition. Please try again.');
                });
        });
    });

    // add event listener to dropdowns to populate size dropdowns if allocation modal is open
    const flavorSelects = document.querySelectorAll('[id^="allocation-flavor"]');
    // check if allocation modal is open
    flavorSelects.forEach(select => {
        select.addEventListener('change', handleSize);
        select.addEventListener('change', () => { handleCheckAvailability(select); });
    });

});

// Function to populate the size dropdown based on the selected flavor
function handleSize(event) {
    const flavorSelect = event.target;
    const selectedFlavor = flavorSelect.value;
    const flavorSelectId = flavorSelect.id;
    const sizeSelectId = flavorSelectId.replace('flavor', 'container-size');
    const sizeSelect = document.getElementById(sizeSelectId);

    // Clear the size dropdown
    sizeSelect.innerHTML = '<option value="" disabled selected>Choose...</option>';

    // If a flavor is selected, fetch the sizes for that flavor
    if (selectedFlavor) {
        fetch(`/orders/fetch_sizes?flavor=${encodeURIComponent(selectedFlavor)}`)
            .then(response => response.json())
            .then(data => {
                data.sizes.forEach(size => {
                    const option = document.createElement('option');
                    option.value = size;
                    option.textContent = capitalize(size);
                    sizeSelect.appendChild(option);
                });
            });
    }
}

// Function to handle the max quantity input based on available stock
function handleCheckAvailability(flavorSelect) {
    const sizeSelect = flavorSelect.parentElement.parentElement.nextElementSibling.querySelector('.allocation-container-size');
    const quantityInput = sizeSelect.parentElement.parentElement.nextElementSibling.querySelector('.allocation-quantity');
    const quantityLabel = quantityInput.parentElement.querySelector('label');

    sizeSelect.addEventListener('change', () => {
        checkAvailable(flavorSelect, sizeSelect, quantityInput, quantityLabel);
    });
}

// Function to update the max quantity input based on flavor and size
function checkAvailable(flavorSelect, sizeSelect, quantityInput, quantityLabel) {
    const selectedFlavor = flavorSelect.value;
    const selectedSize = sizeSelect.value;

    console.log(flavorSelect, sizeSelect, quantityInput, quantityLabel);

    if (selectedFlavor && selectedSize && (sizeSelect.value !== 'Choose...')) {
        fetch(`/orders/fetch_stock?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);

                // Display and set the max quantity for the selected flavor and size
                if (data.status === 'planned' && flavorSelect.value !== 'Choose...') {
                    msg = `Next batch for ${selectedFlavor} (${selectedSize}) available on ${data.dock_date}. Please select a different flavor or size.`;
                    alert(msg);

                    // clear the flavor and size select inputs
                    flavorSelect.options[0].selected = true;
                    sizeSelect.options[0].selected = true;

                    // remove event listener to prevent re-alerting
                    sizeSelect.removeEventListener('change', () => {
                        checkAvailable(flavorSelect, sizeSelect, quantityInput, quantityLabel);
                    });
                } else {
                    quantityLabel.textContent = `Quantity (max: ${data.stock})`;
                    quantityInput.max = data.stock;
                }

            })
            .catch(error => {
                console.error('Error checking available stock:', error);
                alert('Failed to load available stock. Please try again.');

                // clear the flavor and size select inputs
                flavorSelect.options[0].selected = true;
                sizeSelect.options[0].selected = true;
            });
    }
}


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

    if (selectedFlavor && selectedSize && (sizeSelect.value !== 'Choose...')) {
        
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

    // set transaction id to hidden input fields
    const hiddenInput = document.getElementById('product-id');
    const hiddenInput2 = document.getElementById('product-id-delete');

    if (hiddenInput) {
        hiddenInput.value = parseInt(productId);
        hiddenInput2.value = parseInt(productId);
    }

    // set product id input field to current product id
    const productIdInput = document.getElementById('product-id');

    if (productIdInput) {
        productIdInput.value = productId;
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

        // skip non-modifiable attributes
        const inputField = document.getElementById(`product-${attribute.replace('_', '-')}`);

        // set input field value to current product attribute value
        if (inputField) {
            if (inputField.id === 'product-price') {

                // format price to 2 decimal places
                inputField.value = parseFloat(product_content[attribute]).toFixed(2);
            } else if (inputField.id === 'product-dock-date') {

                // format date for input field
                const dbDate = product_content[attribute.replace('-', '_')]
                const formattedDate = dbDate.split('/').reverse().join('-');
                inputField.value = formattedDate;
                console.log(formattedDate);
            } else {
                inputField.value = product_content[attribute];
            }
        }
    });

    $('#productModal').modal('show'); // Show the modal
}

function closeModal() {
    $('#productModal').modal('hide'); // Hide the modal
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}