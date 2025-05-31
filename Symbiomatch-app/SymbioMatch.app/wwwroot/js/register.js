$(document).ready(function () {
    // Bind the submit event of the form
    $('#register-form').on('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Gather form data
        const formData = new FormData(this);
        const companyType = formData.get("companyType");

        // Handle new company registration
        if (companyType === "new") {
            const address = getAddressFromForm();
            getCoordinates(address, function (coordinates) {
                if (coordinates) {
                    formData.set("lat", coordinates.lat);
                    formData.set("lng", coordinates.lng);
                    sendAjaxRequest(formData); // Send AJAX request
                } else {
                    alert("Invalid address");
                }
            });
        } else {
            sendAjaxRequest(formData); // Send AJAX request for existing company
        }
    });

    // Send AJAX request
    function sendAjaxRequest(formData) {
        $.ajax({
            url: '/register',
            type: 'POST',
            data: formData,
            contentType: false, 
            processData: false, 
            success: function (response) {
                // Handle success response
                if (response.success) {
                    window.location.href = '/';
                } else {
                    alert("Registration failed: " + response.message);
                }
            },
            error: function (xhr, status, error) {
                // Handle AJAX error
                console.error("Error:", status, error);
                alert("There was an error processing your request.");
            }
        });
    }

    // Get the full address from the form
    function getAddressFromForm() {
        const address = $('#address').val();
        const postalCode = $('#postalCode').val();
        const city = $('#city').val();
        const country = $('#country').val();
        return `${address}, ${postalCode}, ${city}, ${country}`;
    }

    // Function to get coordinates (using Google Maps API)
    function getCoordinates(address, callback) {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: address }, function (results, status) {
            if (status === 'OK') {
                const location = results[0].geometry.location;
                callback({ lat: location.lat(), lng: location.lng() });
            } else {
                console.error('Geocoding failed: ' + status);
                callback(null);
            }
        });
    }

    // Toggle visibility of new company-specific fields
    function toggleNewCompanyFields() {
        const newCompanyFields = $('#new-company-fields');
        newCompanyFields.toggle();
    }
});
