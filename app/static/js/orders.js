// function to open the modal
function openModal(order_content, orderId) {

    $('#customersUpdateModal').modal('show'); // Show the modal

    // console.log("Modal opened");
}


// function to close the modal
function closeModal() {
    $('#customersUpdateModal').modal('hide'); // Hide the modal

    // console.log("Modal closed");
}

// handle dynamic content in the modal
document.addEventListener('DOMContentLoaded', function() {

    // SIZE SELECTION DROPDOWN POPULATION
    handleSize();

    // COST DISPLAY BASED ON FLAVOR/CONTAINER SIZE SELECTION
    handleCost()

    // MAX QUANTITY INPUT BASED ON AVAILABLE STOCK
    handleMaxQuantity();

});


// function to handle the max quantity input based on available stock
function handleMaxQuantity() {

    // get the flavor and size inputs
    const flavorSelect = document.getElementById('flavor');
    const sizeSelect = document.getElementById('container-size');

    // add event listeners to the flavor and size dropdowns
    // flavorSelect.addEventListener('change', () => updateMaxQuantity(flavorSelect, sizeSelect));
    sizeSelect.addEventListener('change', () => updateMaxQuantity(flavorSelect, sizeSelect));

}

// function to update the max quantity based on flavor and size
function updateMaxQuantity(flavorSelect, sizeSelect) {

    // get the quantity input and the max quantity display
    const quantityInput = document.getElementById('quantity');
    const maxQuantityDisplay = document.getElementById('max-quantity');
    const maxQuantityDisplayContainer = document.getElementById('max-quantity-container');

    const selectedFlavor = flavorSelect.options[flavorSelect.selectedIndex].text;
    const selectedSize = sizeSelect.options[sizeSelect.selectedIndex].text;

    // if both flavor and size are selected, fetch the stock for that combination
    if (selectedFlavor && selectedSize) {

        fetch(`/orders/fetch_stock?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
            .then(response => response.json())
            .then(data => {

                // show the max quantity display container
                maxQuantityDisplayContainer.hidden = false;

                // display the stock as the max quantity
                maxQuantityDisplay.textContent = data.stock;

                // set the max attribute of the quantity input to the stock
                quantityInput.max = data.stock;
            })
            .catch(error => {

                // log the error and alert the user
                console.error('Error fetching stock:', error);
                alert('Failed to load stock. Please try again.');

            });
    }
}


// function to trigger the cost display based on the quantity, flavor, and size inputs
function handleCost() {

    // get the relevant inputs
    const quantityInput = document.getElementById('quantity');
    const flavorInput = document.getElementById('flavor');
    const sizeInput = document.getElementById('container-size');

    // add event listeners to the inputs to trigger updates to the cost display
    quantityInput.addEventListener('input', () => updateCost(quantityInput, flavorInput, sizeInput));
    flavorInput.addEventListener('change', () => updateCost(quantityInput, flavorInput, sizeInput));
    sizeInput.addEventListener('change', () => updateCost(quantityInput, flavorInput, sizeInput));

}


// function to update the cost display based on the quantity, flavor, and size inputs
function updateCost(quantityInput, flavorInput, sizeInput) {

    // get the values of the relevant inputs and the cost display element
    const costDisplay = document.getElementById('cost-display');
    const quantity = quantityInput.value;
    const flavor = flavorInput.value;
    const size = sizeInput.value;

    // if all three inputs have values, fetch the cost
    if (quantity && flavor && size && (quantity > 0)) {

        fetch(`/orders/fetch_cost?flavor=${encodeURIComponent(flavor)}&container-size=${encodeURIComponent(size)}&quantity=${quantity}`)
            .then(response => response.json())
            .then(data => {

                // display the cost
                costDisplay.textContent = data.cost;
            })
            .catch(error => {

                // log the error and alert the user
                console.error('Error fetching cost:', error);
                alert('Failed to load cost. Please try again.');

            });
    }

}


// function to populate the size dropdown based on the selected flavor
function handleSize() {

    // get the flavor and size dropdowns
    const flavorSelect = document.getElementById('flavor');
    const containerSizeSelect = document.getElementById('container-size');

    // add an event listener to the flavor dropdown
    flavorSelect.addEventListener('change', function() {

        // get the inner text of the selected option
        const selectedFlavor = flavorSelect.options[flavorSelect.selectedIndex].text;

        // set the flavor input value to the selected flavor
        document.getElementById('flavor').value = selectedFlavor;

        // clear the size dropdown
        containerSizeSelect.innerHTML = '<option value="">Select size</option>'; // TODO: disable this option

        // if a flavor is selected, fetch the sizes for that flavor
        if (selectedFlavor) {

            // query the server for the sizes of the selected flavor
            fetch(`/orders/fetch_sizes?flavor=${encodeURIComponent(selectedFlavor)}`)
                .then(response => response.json())
                .then(data => {

                    // populate the size dropdown with the sizes
                    data.sizes.forEach(size => {
                        const option = document.createElement('option');
                        option.value = size;
                        option.textContent = size;
                        containerSizeSelect.appendChild(option);
                    });

                })
                .catch(error => {

                    // log the error and alert the user
                    console.error('Error fetching sizes:', error);
                    alert('Failed to load sizes. Please try again.');

                });
        }
    });
}