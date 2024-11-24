document.addEventListener('DOMContentLoaded', function() {

    const addLineItemButton = document.getElementById('add-line-item');
    const lineItemsContainer = document.getElementById('line-items-container');
    let lineItemCount = 1;

    function addLineItem() {
        const flavorSelect = document.getElementById('flavor-0');
        const lineItem = document.createElement('div');
        lineItem.classList.add('line-item', 'mb-3', 'row');
        lineItem.innerHTML = `
            <hr style="border-top: 2px dotted #000;">
            <h5>Line Item ${lineItemCount + 1}</h5>
            <div class="col-md-3">
                <label for="flavor-${lineItemCount}" class="form-label">Flavor</label>
                <select class="form-control flavor" id="flavor-${lineItemCount}" name="order_items[${lineItemCount}][flavor]" required>
                    ${flavorSelect.innerHTML}
                </select>
            </div>
            <div class="col-md-3">
                <label for="container-size-${lineItemCount}" class="form-label">Container Size</label>
                <select class="form-control container-size" id="container-size-${lineItemCount}" name="order_items[${lineItemCount}][container-size]" required>
                    <option value="" disabled selected>Select size</option>
                    <!-- Options will be populated dynamically -->
                </select>
            </div>
            <div class="col-md-3">
                <label for="quantity-${lineItemCount}" class="form-label">Quantity <span class="max-quantity-container" id="max-quantity-container-${lineItemCount}" hidden><b>(max: <span class="max-quantity" id="max-quantity"></span>)</b></span></label>
                <input 
                    type="number" 
                    class="form-control quantity" 
                    id="quantity-${lineItemCount}" 
                    name="order_items[${lineItemCount}][quantity]" 
                    min="1" step="1"
                    oninput="this.value = this.value.replace(/\D/g, '')"
                    required>
            </div>
            <div class="col-md-3">
                <label for="line-item-cost-${lineItemCount}" class="form-label">Line Item Cost</label>
                <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control line-item-cost" id="line-item-cost-${lineItemCount}" name="order_items[${lineItemCount}][line-item-cost]" step="0.01" readonly>
                </div>
            </div>
        `;
        lineItemsContainer.appendChild(lineItem);
        lineItemCount++;

        // Show the "Delete Line Item" button
        deleteLineItemButton.hidden = false;

        // Add event listener to the new flavor select
        const newFlavorSelect = lineItem.querySelector('.flavor');
        newFlavorSelect.addEventListener('change', handleSize);
        newFlavorSelect.addEventListener('change', handleCost);

        // Add event listener to the new flavor select
        handleMaxQuantity(newFlavorSelect);
        handleCost(newFlavorSelect);
    }

    // Add event listener to the "Add Line Item" button
    addLineItemButton.addEventListener('click', addLineItem);

    // Function to delete the most recent line item
    function deleteMostRecentLineItem() {
        const lineItems = document.querySelectorAll('.line-item');
        if (lineItems.length > 1) { // Ensure at least one line item remains
            const mostRecentLineItem = lineItems[lineItems.length - 1];
            mostRecentLineItem.remove();
            lineItemCount--;

            // trigger the cost display update
            updateTotalCost();
        } 
        
        // if only one line item remains, hide the "Delete Line Item" button
        if (lineItemCount === 1) {
            deleteLineItemButton.hidden = true;
        } 
    }

    // Add event listener to the "Delete Line Item" button
    const deleteLineItemButton = document.getElementById('delete-line-item');
    deleteLineItemButton.addEventListener('click', deleteMostRecentLineItem);

    // Function to populate the size dropdown based on the selected flavor
    function handleSize(event) {
        const flavorSelect = event.target;
        const selectedFlavor = flavorSelect.value;
        const flavorSelectId = flavorSelect.id;
        const sizeSelectId = flavorSelectId.replace('flavor', 'container-size');
        const sizeSelect = document.getElementById(sizeSelectId);

        // Clear the size dropdown
        sizeSelect.innerHTML = '<option value="" disabled selected>Select size</option>';

        // If a flavor is selected, fetch the sizes for that flavor
        if (selectedFlavor) {
            fetch(`/orders/fetch_sizes?flavor=${encodeURIComponent(selectedFlavor)}`)
                .then(response => response.json())
                .then(data => {
                    data.sizes.forEach(size => {
                        const option = document.createElement('option');
                        option.value = size;
                        option.textContent = size;
                        sizeSelect.appendChild(option);
                    });
                });
        }
    }

    // Function to handle the max quantity input based on available stock
    function handleMaxQuantity(flavorSelect) {
        const sizeSelect = flavorSelect.parentElement.nextElementSibling.querySelector('.container-size');
        const quantityInput = sizeSelect.parentElement.nextElementSibling.querySelector('.quantity');
        const maxQuantityDisplay = quantityInput.parentElement.querySelector('.max-quantity');
        const maxQuantityDisplayContainer = maxQuantityDisplay.parentElement.parentElement; // grandparent element because of the b tag

        flavorSelect.addEventListener('change', () => {
            updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, maxQuantityDisplay, maxQuantityDisplayContainer);
        });

        sizeSelect.addEventListener('change', () => {
            updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, maxQuantityDisplay, maxQuantityDisplayContainer);
        });
    }

    // Function to update the max quantity input based on flavor and size
    function updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, maxQuantityDisplay, maxQuantityDisplayContainer) {
        const selectedFlavor = flavorSelect.value;
        const selectedSize = sizeSelect.value;

        if (selectedFlavor && selectedSize && (sizeSelect.value !== 'Select size')) {
            fetch(`/orders/fetch_stock?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
                .then(response => response.json())
                .then(data => {
                    maxQuantityDisplayContainer.hidden = false;
                    maxQuantityDisplay.textContent = data.stock;
                    quantityInput.max = data.stock;
                })
                .catch(error => {
                    console.error('Error fetching stock:', error);
                    alert('Failed to load stock. Please try again.');
                });
        }
    }

    // Function to trigger the cost display based on the quantity, flavor, and size inputs
    function handleCost(flavorSelect) {
        const flavorSelectId = flavorSelect.id;
        const sizeSelect = document.getElementById(flavorSelectId.replace('flavor', 'container-size'));
        const quantityInput = sizeSelect.parentElement.nextElementSibling.querySelector('.quantity');

        quantityInput.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
        flavorSelect.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
        sizeSelect.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
    }

    // Function to update the cost display based on the quantity, flavor, and size inputs
    function updateCost(quantityInput, flavorInput, sizeInput) {
        const lineItemCostInput = quantityInput.parentElement.nextElementSibling.querySelector('input');
        const quantity = quantityInput.value;
        const flavor = flavorInput.value;
        const size = sizeInput.value;

        if (quantity && flavor && size && (quantity > 0)) {
            fetch(`/orders/fetch_cost?flavor=${encodeURIComponent(flavor)}&container-size=${encodeURIComponent(size)}&quantity=${quantity}`)
                .then(response => response.json())
                .then(data => {
                    lineItemCostInput.value = data.cost.toFixed(2);

                    // sum all line item costs to get the total cost
                    updateTotalCost();
                })
                .catch(error => {
                    console.error('Error fetching cost:', error);
                    alert('Failed to load cost. Please try again.');
                });
        }
    }

    // Function to update the cost display
    function updateTotalCost() {
        const allLineItemCostInputs = document.querySelectorAll('.line-item-cost');
        const costDisplay = document.getElementById('cost-display');
        let totalCost = 0;

        // Sum all line item costs
        allLineItemCostInputs.forEach(lineItemCostInput => {
            if (lineItemCostInput.value) {
                totalCost += parseFloat(lineItemCostInput.value);
            }
        });

        // Add the shipping cost to the total cost
        const shippingCostInput = document.getElementById('shipping-cost');
        if (shippingCostInput.value) {
            totalCost += parseFloat(shippingCostInput.value);
        }

        // Display the total cost
        costDisplay.textContent = totalCost.toFixed(2);

        // Update the total cost hidden input
        const totalCostInput = document.getElementById('total-cost');
        totalCostInput.value = totalCost.toFixed(2);
    }

    // Function to set the shipping date depending on the shipping type
    // TODO: Implement in AdminConfigs
    function setShippingDate() {
        const shippingTypeSelect = document.getElementById('shipping-type');
        const shippingDateInput = document.getElementById('shipping-date');
        const expressMinDayGap = 5; // 5 days TODO: Implement in AdminConfigs
        const standardMinDayGap = 10; // 10 days

        const currentDate = new Date();
        const selectedShippingType = shippingTypeSelect.value;
        let minDayGap;

        if (selectedShippingType === 'express') {
            minDayGap = expressMinDayGap;
        } else {
            minDayGap = standardMinDayGap;
        }

        const minDate = new Date(currentDate);
        minDate.setDate(currentDate.getDate() + minDayGap);

        const minMonth = minDate.getMonth() + 1;
        const minDay = minDate.getDate();
        const minYear = minDate.getFullYear();

        const formattedMinDate = `${minMonth}/${minDay}/${minYear}`;
        shippingDateInput.value = formattedMinDate;
    }

    // Function to set the shipping cost depending on the shipping type
    function setShippingCost() {
        const shippingTypeSelect = document.getElementById('shipping-type');
        const shippingCostInput = document.getElementById('shipping-cost');

        // Get the selected shipping type
        const selectedOption = shippingTypeSelect.options[shippingTypeSelect.selectedIndex];
        const shippingCost = selectedOption.getAttribute('data-cost');

        // Set the shipping cost based on the selected shipping type
        if (shippingCost) {
            shippingCostInput.value = parseFloat(shippingCost).toFixed(2);
        } else {
            shippingCostInput.value = '0.00';
        }

        // trigger the total cost update
        updateTotalCost();
    }

    // Add event listener to the shipping type select
    const shippingTypeSelect = document.getElementById('shipping-type');
    shippingTypeSelect.addEventListener('change', setShippingDate);
    shippingTypeSelect.addEventListener('change', setShippingCost);

    // Add event listeners to the inputs in the first line item
    const firstFlavorSelect = document.getElementById('flavor-0');
    firstFlavorSelect.addEventListener('change', handleSize);
    handleMaxQuantity(firstFlavorSelect);
    handleCost(firstFlavorSelect);



    // add event listeners to the table rows
    // const ordersTable = document.getElementById('orders-table');
    // const tableRows = ordersTable.querySelectorAll('tr');
    // tableRows.forEach(row => {
    //     row.addEventListener('click', () => {
    //         const orderId = row.getAttribute('id');
    //         const orderContent = row.getAttribute('data-content');
    //         populateOrdersModal(orderContent, orderId);
    //     });
    // });

});

// function to open the view/edit order modal
function openOrderUpdateModal(order_id) {
    const orderIdInput = document.getElementById('order-id-update');
    const orderIdInputHidden = document.getElementById('order-id-update-hidden');

    // Set the order id and content in the modal
    if (order_id) {
        orderIdInput.value = parseInt(order_id);
        orderIdInputHidden.value = parseInt(order_id);
    }

    // fetch the order info from the server
    fetch(`/orders/fetch_order_info?order_id=${order_id}`)
        .then(response => response.json())
        .then(data => {
            const orderContent = data;
            console.log(data);

            // Set the customer name
            const customerNameInput = document.getElementById('customer-update');
            customerNameInput.value = orderContent.customer;

            // Set the shipping type, date, and cost
            const shippingTypeSelect = document.getElementById('shipping-type-update');
            const shippingDateInput = document.getElementById('shipping-date-update');
            const shippingCostInput = document.getElementById('shipping-cost-update');
            shippingTypeSelect.value = orderContent.shipping_type.charAt(0).toUpperCase() + orderContent.shipping_type.slice(1);
            
            const shippingDate = new Date(orderContent.shipping_date);
            const formattedShippingDate = `${shippingDate.getMonth() + 1}/${shippingDate.getDate() + 1}/${shippingDate.getFullYear()}`;
            shippingDateInput.value = formattedShippingDate;

            shippingCostInput.value = `$${parseFloat(orderContent.shipping_cost).toFixed(2)}`;

        })
        .catch(error => {
            console.error('Error fetching order:', error);
            alert('Failed to load order. Please try again.');
        });

    $('#ordersUpdateModal').modal('show');
}


// function to change all inputs in the view/edit order modal from readonly to editable
function toggleEdit() {

    // get all input fields in the modal
    const updateModal = document.getElementById('ordersUpdateModal');
    const inputs = updateModal.querySelectorAll('.order-input');
    const updateInputs = updateModal.querySelectorAll('[id*="-update"]');
    updateInputs.forEach(input => {
        input.readOnly = !input.readOnly;
        if (input.classList.contains('form-control-plaintext')) {
            input.classList.remove('form-control-plaintext');
            input.classList.add('form-control');
        } else {
            input.classList.remove('form-control');
            input.classList.add('form-control-plaintext');
        }
    });

    // toggle the readonly attribute of each input
    inputs.forEach(input => {
        input.readOnly = !input.readOnly;
    });

    // toggle the hidden attribute of the "Save Changes" button
    // const saveChangesButton = document.getElementById('save-changes');
    // saveChangesButton.hidden = !saveChangesButton.hidden;

}