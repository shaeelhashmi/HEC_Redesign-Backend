async function verifyUser(userEmail) {
    // 1. Ask for the CNIC number
  // Sanitize the email to match the HTML ID format
    const sanitizedEmail = userEmail.replace('@', '_').replace(/\./g, '_');
    const cnicInput = document.getElementById(`cnic_input_${sanitizedEmail}`);
    const cnicNumber = cnicInput.value.trim();
    if (!cnicNumber || cnicNumber.length !== 13 || !/^\d+$/.test(cnicNumber)) {
        alert("Please enter a valid 13-digit CNIC number without dashes.");
        return;
    }
    const response = await fetch(`/admin/verify_user/${userEmail}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cnic_number: cnicNumber })
    });
    if (response.ok) {
        alert("User verified successfully!");
        location.reload();
    } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
    }
}