document.addEventListener('DOMContentLoaded', async () => {
  await window.Clerk.load();

  const btn = document.getElementById('verify_cnic');
  
  if (btn) {
    btn.addEventListener('click', async () => {
      // FIX: Changed 'cnic_image_input' to 'cnic' to match your HTML ID
      const fileInput = document.getElementById('cnic'); 
      
      // Check if a file was actually selected to avoid errors
      if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select an image first");
        return;
      }

      const token = await window.Clerk.session.getToken();
      const formData = new FormData();
      
      // 'cnic_image' is the key Flask will look for in request.files
      formData.append('cnic_image', fileInput.files[0]); 

      const res = await fetch('/api/verify-cnic', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      const data = await res.json();
      console.log('Response from server:', data);
    });
  }
});