document.addEventListener('DOMContentLoaded', function() {
    const shippingAddress = document.getElementById('shipping-address');
    const billingAddress = document.getElementById('billing-address');
    const billingCheckbox = document.getElementById('billing-checkbox');

    // Function to toggle billing address
    function toggleBillingAddress() {
        if (billingCheckbox.checked) {
            billingAddress.innerText = shippingAddress.value;
            billingAddress.value = shippingAddress.value;
            billingAddress.readOnly = true;
        } else {
            billingAddress.readOnly = false;
            billingAddress.innerText = ''; // Optional: Clear billing address when unchecked
            billingAddress.value = '';
        }
    }

    // Event listener for checkbox change
    billingCheckbox.addEventListener('change', toggleBillingAddress);

    // Event listener for shipping address input
    shippingAddress.addEventListener('input', function() {
        if (billingCheckbox.checked) {
            billingAddress.innerText = shippingAddress.value;
        }
    });

    // Initialize billing address state on page load
    toggleBillingAddress();
});