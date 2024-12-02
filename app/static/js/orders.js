document.addEventListener('DOMContentLoaded', function() {

    // open the update order modal if the order_id is in the url
    const urlParams = new URLSearchParams(window.location.search);
    const shipment_id = urlParams.get('shipment_id');
    if (shipment_id) {
        console.log('shipment_id:', shipment_id);
        document.getElementById(`shipment-${shipment_id}`).click();
    }

    // Add event listener to the "Add Line Item" button
    const addLineItemButton = document.getElementById('add-line-item');
    addLineItemButton.addEventListener('click', () => addLineItem(false));

    // Add event listener to the "Delete Line Item" button
    const deleteLineItemButton = document.getElementById('delete-line-item');
    deleteLineItemButton.addEventListener('click', () => deleteMostRecentLineItem(false));

    // set an event listener for the add/delete line-item buttons
    const updateAddLineItemButton = document.getElementById('update-add-line-item');
    updateAddLineItemButton.addEventListener('click', () => addLineItem(true));

    const updateDeleteLineItemButton = document.getElementById('update-delete-line-item');
    updateDeleteLineItemButton.addEventListener('click', () => deleteMostRecentLineItem(true));

    // Add event listener to toggle the edit mode of the view/edit order modal when it is closed
    const orderUpdateModal = document.getElementById('ordersUpdateModal');
    orderUpdateModal.addEventListener('hidden.bs.modal', function(event) {
        // Check if the modal was closed by clicking the close button or clicking away
        if (event.target === orderUpdateModal) {
            toggleEdit(false);
        }
    });

    // Function to set the shipping date depending on the shipping type
    // TODO: Implement in AdminConfigs (use a fetch request to get the min day gap)
    function setShippingDate() {
        const shippingTypeSelect = document.getElementById('shipping-type');
        const shippingDateInput = document.getElementById('expected-shipping-date');
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
    // TODO: Implement in AdminConfigs (use a fetch request to get the shipping cost)
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
        updateTotalCost(false);
    }

    // Add event listener to the shipping type select
    const shippingTypeSelect = document.getElementById('shipping-type');
    shippingTypeSelect.addEventListener('change', setShippingDate);
    shippingTypeSelect.addEventListener('change', setShippingCost);

    // Add event listeners to the inputs in the first line item
    const firstFlavorSelect = document.getElementById('flavor-0');
    firstFlavorSelect.addEventListener('change', handleSize);

    // Call the handleSize and handleCost functions to populate the size dropdown and set the cost
    handleMaxQuantity(firstFlavorSelect);
    handleCost(firstFlavorSelect);

});


// Function to add a new line item to the order form 
function addLineItem(isUpdateModal) {

    // create a new line item div
    const lineItem = document.createElement('div');

    // set the class of the new line item
    if (isUpdateModal) {
        lineItem.classList.add('update-line-item', 'mb-3', 'row');
    } else {
        lineItem.classList.add('line-item', 'mb-3', 'row');
    }

    // get the first line item to replace the 0s with the current line item count
    const lineItemsContainer = document.getElementById(isUpdateModal ? 'update-line-items-container' : 'line-items-container');
    const deleteLineItemButton = document.getElementById(isUpdateModal ? 'update-delete-line-item' : 'delete-line-item');
    const lineItemCount = document.querySelectorAll(isUpdateModal ? '.update-line-item' : '.line-item').length;
    const firstLineItem = document.getElementById(isUpdateModal ? "update-first-line-item" : "first-line-item");

    console.log("begin", document.querySelectorAll(isUpdateModal ? '.update-line-item' : '.line-item'));

    // replace all instances of the number 0 with the current line item count
    lineItem.innerHTML = firstLineItem.innerHTML.replace(/(id|name|for)="([^"]*?)0([^"]*?)"/g, function(match, p1, p2, p3) {
        return `${p1}="${p2}${lineItemCount}${p3}"`;
    });

    // replace the h5 tag with the current line item count
    lineItem.innerHTML = lineItem.innerHTML.replace(/Line Item \d+/g, `Line Item ${lineItemCount + 1}`);

    // add a dotted line above the new line item
    lineItem.innerHTML = `
        <hr style="border-top: 2px dotted #000;">
    ` + lineItem.innerHTML;

    // append the new line item to the line items container
    lineItemsContainer.appendChild(lineItem);

    // Show the "Delete Line Item" button
    deleteLineItemButton.hidden = false;

    // Add event listener to the new flavor select
    const newFlavorSelect = lineItem.querySelector('.flavor');
    newFlavorSelect.addEventListener('change', handleSize);
    newFlavorSelect.addEventListener('change', handleCost);

    // Call the handleSize and handleCost functions to populate the size dropdown and set the cost
    handleMaxQuantity(newFlavorSelect);
    handleCost(newFlavorSelect);

    console.log(lineItemCount);
}


// Function to delete the most recent line item
function deleteMostRecentLineItem(isUpdateModal) {

    // get all line items and the delete line item button
    const lineItems = document.querySelectorAll(isUpdateModal ? '.update-line-item' : '.line-item');
    const deleteLineItemButton = document.getElementById(isUpdateModal ? 'update-delete-line-item' : 'delete-line-item');
    const lineItemCount = lineItems.length;

    // remove the most recent line item
    if (lineItems.length > 1) { // Ensure at least one line item remains
        const mostRecentLineItem = lineItems[lineItems.length - 1];
        mostRecentLineItem.remove();

        // trigger the cost display update
        updateTotalCost(isUpdateModal);
    } 
    
    // if only one line item remains, hide the "Delete Line Item" button
    // TODO: investigate whether this works
    if (lineItemCount === 1) {
        deleteLineItemButton.hidden = true;
    }

    console.log(lineItemCount);
}


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
function handleMaxQuantity(flavorSelect) {
    const sizeSelect = flavorSelect.parentElement.parentElement.nextElementSibling.querySelector('.container-size');
    const quantityInput = sizeSelect.parentElement.parentElement.nextElementSibling.querySelector('.quantity');
    const quantityLabel = quantityInput.parentElement.querySelector('label');

    flavorSelect.addEventListener('change', () => {
        updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, quantityLabel);
    });

    sizeSelect.addEventListener('change', () => {
        updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, quantityLabel);
    });
}


// Function to update the max quantity input based on flavor and size
function updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, quantityLabel) {
    const selectedFlavor = flavorSelect.value;
    const selectedSize = sizeSelect.value;

    if (selectedFlavor && selectedSize && (sizeSelect.value !== 'Choose...')) {
        fetch(`/orders/fetch_stock?flavor=${encodeURIComponent(selectedFlavor)}&container-size=${encodeURIComponent(selectedSize)}`)
            .then(response => response.json())
            .then(data => {

                // Display and set the max quantity for the selected flavor and size
                quantityLabel.textContent = `Quantity (max: ${data.stock})`;
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
    let sizeSelect;
    let quantityInput;

    if (flavorSelectId.includes('update')) {
        sizeSelect = flavorSelect.parentElement.parentElement.nextElementSibling.querySelector('.container-size');
        quantityInput = sizeSelect.parentElement.parentElement.nextElementSibling.querySelector('.quantity');
    } else {
        sizeSelect = document.getElementById(flavorSelectId.replace('flavor', 'container-size'));
        quantityInput = sizeSelect.parentElement.parentElement.nextElementSibling.querySelector('.quantity');
    }

    if (flavorSelect && quantityInput && sizeSelect) {
        quantityInput.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
        flavorSelect.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
        sizeSelect.addEventListener('change', () => updateCost(quantityInput, flavorSelect, sizeSelect));
    } else {
        console.error('Error fetching cost: missing inputs');
    }
}


// Function to update the cost display based on the quantity, flavor, and size inputs
function updateCost(quantityInput, flavorInput, sizeInput) {
    const lineItemCostInput = quantityInput.parentElement.parentElement.nextElementSibling.querySelector('input');
    const quantity = quantityInput.value;
    const flavor = flavorInput.value;
    const size = sizeInput.value;

    if (quantity && flavor && size && (quantity > 0)) {
        fetch(`/orders/fetch_cost?flavor=${encodeURIComponent(flavor)}&container-size=${encodeURIComponent(size)}&quantity=${quantity}`)
            .then(response => response.json())
            .then(data => {
                lineItemCostInput.value = data.cost.toFixed(2);

                // sum all line item costs to get the total cost
                if (lineItemCostInput.id.includes('update')) {
                    updateTotalCost(true);
                } else {
                    updateTotalCost(false);
                }

            })
            .catch(error => {
                console.error('Error fetching cost:', error);
                alert('Failed to load cost. Please try again.');
            });
    }
}


// Function to update the cost display
function updateTotalCost(isUpdateModal) {

    const costDisplay = document.getElementById(isUpdateModal ? 'update-cost-display' : 'cost-display');
    let allLineItemCostInputs = document.querySelectorAll(isUpdateModal ? '.update-line-item-cost' : '.line-item-cost');
    const shippingCostInput = document.getElementById(isUpdateModal ? 'shipping-cost-update' : 'shipping-cost');

    let totalCost = 0;
    // Sum all line item costs
    allLineItemCostInputs.forEach(lineItemCostInput => {
        if (lineItemCostInput.value) {
            totalCost += parseFloat(lineItemCostInput.value);
        }
    });

    // Add the shipping cost to the total cost
    if (shippingCostInput.value) {
        totalCost += parseFloat(shippingCostInput.value);
    }

    // Display the total cost
    costDisplay.textContent = totalCost.toFixed(2);

    // Update the total cost hidden input
    let totalCostInput;
    if (isUpdateModal) {
        totalCostInput = document.getElementById('order-total-cost-hidden');
    } else {
        totalCostInput = document.getElementById('total-cost');
    }
    totalCostInput.value = totalCost.toFixed(2);
}


// function to open the view/edit order modal
function openOrderUpdateModal(order_id) {

    // update the shipment details navigation button
    const navShipmentBtn = document.getElementById('nav-shipment-btn');
    navShipmentBtn.href = `/shipments?order_id=${order_id}`;

    // reset the url params
    window.history.replaceState({}, document.title, "/orders");

    // set the order id in the hidden input fields
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

            if ('error' in orderContent) {
                alert(`Failed to load order. ${orderContent}. Please contact support.`);
                return;
            }

            // Set the customer name
            const customerNameInput = document.getElementById('customer-update');
            customerNameInput.value = orderContent.customer;

            // Set the shipping type, date, and cost
            document.getElementById('shipping-type-update').value = capitalize(orderContent.shipping_type);
            document.getElementById('expected-shipping-date-update').value = orderContent.expected_shipping_date;
            document.getElementById('shipping-cost-update').value = parseFloat(orderContent.shipping_cost).toFixed(2);
            document.getElementById('shipping-cost-update').parentElement.querySelector('label').textContent = 'Shipping Cost ($)';

            // set the desired receipt date and order creation date
            document.getElementById('desired-receipt-date-update').value = orderContent.desired_receipt_date;
            document.getElementById('order-creation-date-update').value = orderContent.order_creation_date;

            // set the shipping/billing addresses
            document.getElementById('shipping-address-update').value = orderContent.shipping_address;
            document.getElementById('billing-address-update').value = orderContent.billing_address;

            // set the hidden order id for the update form
            document.getElementById('order-status-update-hidden').value = orderContent.status;

            // set the order status
            const orderStatusSelect = document.getElementById('order-status-update');
            if (orderContent.status === 'cancelled') {
                const cancelledOption = document.createElement('option');
                cancelledOption.value = 'cancelled';
                cancelledOption.textContent = 'Cancelled';
                cancelledOption.selected = true;
                orderStatusSelect.disabled = true;
                orderStatusSelect.appendChild(cancelledOption);

                // disable the add/delete line item buttons
                const lineItems = document.querySelectorAll('.update-line-item');
                lineItems.forEach(lineItemBtn => {
                    lineItemBtn.disabled = true;
                });

                // disable the cancel order button
                const cancelOrderButton = document.getElementById('cancel-order-btn');
                cancelOrderButton.disabled = true;
            } else {
                const orderStatusOption = Array.from(orderStatusSelect.options).find(option => option.value === orderContent.status);
                if (orderStatusOption) {
                    orderStatusSelect.value = orderStatusOption.value;
                }
            }

            // set the line items
            if (orderContent.line_items && orderContent.line_items.length > 0) {
                const lineItems = orderContent.line_items;
                const lineItemsContainer = document.getElementById('update-line-items-container');
                lineItemsContainer.innerHTML = '';
                lineItems.forEach((lineItem, index) => {
                    const newLineItem = document.createElement('div');
                    newLineItem.classList.add('update-line-item', 'mb-3', 'row');
                    newLineItem.innerHTML = document.getElementById('first-line-item').innerHTML;

                    // get the first line item to replace the 0s with the current line item count
                    newLineItem.innerHTML = newLineItem.innerHTML.replace(/(id|name|for)="([^"]*?)0([^"]*?)"/g, function(match, p1, p2, p3) {
                        return `${p1}="${p2}${index}${p3}"`;
                    });

                    // replace the line item number
                    newLineItem.innerHTML = newLineItem.innerHTML.replace(/Line Item \d+/g, `Line Item ${index + 1}`);

                    // if not the first line item, add a dotted line above the new line item
                    if (index > 0) {
                        newLineItem.innerHTML = `
                            <hr style="border-top: 2px dotted #000;">
                        ` + newLineItem.innerHTML;
                    }

                    // set the line item id
                    if (index === 0) {
                        newLineItem.id = 'update-first-line-item';
                    }

                    // replace the flavor select
                    const flavorSelect = newLineItem.querySelector('.flavor');
                    const flavorOption = Array.from(flavorSelect.options).find(option => option.value === lineItem.flavor);
                    if (flavorOption) {
                        flavorSelect.value = flavorOption.value;
                    }
                    flavorSelect.disabled = true;
                    flavorSelect.id = `flavor-${index}-update`;

                    // append the lineItem size to the sizeSelect options
                    const sizeSelect = newLineItem.querySelector('.container-size');
                    const sizeOption = document.createElement('option');
                    sizeSelect.id = `container-size-${index}-update`;
                    sizeOption.value = lineItem.container_size;
                    sizeOption.textContent = capitalize(lineItem.container_size);
                    sizeOption.selected = true;
                    sizeSelect.disabled = true;
                    sizeSelect.required = true;
                    sizeSelect.appendChild(sizeOption);

                    // replace the quantity input
                    const quantityInput = newLineItem.querySelector('.quantity');
                    quantityInput.id = `quantity-${index}-update`;
                    quantityInput.classList = 'quantity form-control-plaintext';
                    quantityInput.value = lineItem.quantity;
                    quantityInput.required = true;
                    quantityInput.readOnly = true;

                    // replace the payment date input
                    const paymentDateInput = document.getElementById('payment-date-update');
                    paymentDateInput.value = orderContent.payment_date;
                    console.log(orderContent);

                    // event listener to clear line item inputs when flavor is changed
                    flavorSelect.addEventListener('change', () => {
                        sizeSelect.innerHTML = '<option value="" disabled selected>Choose...</option>';
                        quantityInput.value = '';
                        const lineItemCostInput = newLineItem.querySelector('.line-item-cost');
                        lineItemCostInput.value = '';
                    });

                    // set event listeners for the new line item (max quantity, cost)
                    flavorSelect.addEventListener('change', handleSize);
                    handleMaxQuantity(flavorSelect);
                    handleCost(flavorSelect);

                    // replace the cost input
                    const costInput = newLineItem.querySelector('.line-item-cost');
                    costInput.id = `line-item-cost-${index}-update`;
                    costInput.classList = 'update-line-item-cost form-control-plaintext';
                    costInput.value = lineItem.line_item_cost.toFixed(2);
                    costInput.readOnly = true;
                    costInput.required = true;

                    // append the new line item to the line items container
                    lineItemsContainer.appendChild(newLineItem);
                });
            }

            // set the delete form order id
            const hiddenOrderDeleteInput = document.getElementById('order-id-delete');
            hiddenOrderDeleteInput.value = order_id;

            // set the order id for the cancel form
            const hiddenOrderCancelInput = document.getElementById('order-id-cancel');
            hiddenOrderCancelInput.value = order_id;

            // nav to the shipment details if the order has a shipment
            // const shipment_id = orderContent.shipment_id;
            // const navShipmentBtn = document.getElementById('nav-shipment-btn');
            // navShipmentBtn.href = `/shipments?shipment_id=${shipment_id}`;

            // trigger the cost display update
            updateTotalCost(true);

        })
        .catch(error => {
            console.error('Error fetching order:', error);
            alert(`Failed to load order. ${error}.`);
        });

    $('#ordersUpdateModal').modal('show');
}

// function to change all inputs in the view/edit order modal from readonly to editable
function toggleEdit(toEditMode) {

    // get the order status
    const orderStatusSelect = document.getElementById('order-status-update');
    const orderStatus = orderStatusSelect.options[orderStatusSelect.selectedIndex].value;

    // get the update button
    const updateButton = document.getElementById('updateOrderButton');

    // if the update button is disabled and the toEditMode is false, don't toggle the edit mode
    if (!toEditMode && updateButton.disabled) {
        return;
    }

    // toggle the update button to show/hide
    updateButton.disabled = !updateButton.disabled;

    // get all input fields in the modal
    const updateModal = document.getElementById('ordersUpdateModal');
    const updateInputs = updateModal.querySelectorAll('[id*="-update"]');
    let inputsFixedReadOnly = [
        'order-creation-date-update', 'shipping-type-update',
        'expected-shipping-date-update', 'shipping-cost-update',
        'shipping-address-update', 'order-id-update', 'customer-update', 'update-line-items-container'
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


    if (orderStatus !== 'cancelled') {

        // toggle the add/delete line-item buttons to show/hide
        const lineItemButtonsContainer = document.getElementById('update-line-item-buttons-container');
        lineItemButtonsContainer.hidden = !lineItemButtonsContainer.hidden;

        // show the deleteLineItem button if there are more than one line items
        const deleteLineItemButton = document.getElementById('update-delete-line-item');
        const lineItemLength = document.querySelectorAll('.update-line-item').length;
        if (lineItemLength > 1) {
            deleteLineItemButton.hidden = false;
        } else {
            deleteLineItemButton.hidden = true;
        }

        // update the max quantity of the container size input
        const flavorSelects = document.querySelectorAll(".flavor")

        flavorSelects.forEach(flavorSelect => {
            const sizeSelect = flavorSelect.parentElement.parentElement.nextElementSibling.querySelector('.container-size');
            const quantityInput = sizeSelect.parentElement.parentElement.nextElementSibling.querySelector('.quantity');
            const quantityLabel = quantityInput.parentElement.querySelector('label');
        
            updateMaxQuantity(flavorSelect, sizeSelect, quantityInput, quantityLabel);
        })

    }

    // toggle the hidden attribute of the "Save Changes" button
    // const saveChangesButton = document.getElementById('save-changes');
    // saveChangesButton.hidden = !saveChangesButton.hidden;

}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}