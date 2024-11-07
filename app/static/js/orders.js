function openModal(order_content, orderId) {

    $('#customersUpdateModal').modal('show'); // Show the modal

    // console.log("Modal opened");
}

function closeModal() {
    $('#customersUpdateModal').modal('hide'); // Hide the modal

    // console.log("Modal closed");
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