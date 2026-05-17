document.addEventListener('DOMContentLoaded', async () => { // Added 'async' here
    await window.Clerk.load();
    console.log("Checking admin status...");
    try {
        // Ensure Clerk is loaded before calling it
        if (!window.Clerk || !window.Clerk.session) {
            window.location.href = '/login';
            return;
        }

        const token = await window.Clerk.session.getToken();
        console.log("Token retrieved:", token); 
        
        const res = await fetch('/admin/check_admin', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
            // Note: Removed 'body: formData' since your backend doesn't seem to use it, 
            // but you can add it back if you are actually passing a form.
        });

        if (res.ok) {
            const data = await res.json(); // Parse the JSON response
            
            if (data.isAdmin === true) {
                console.log("Access granted: User is an admin.");
                // Let them stay on the page. You can initialize your page logic here.
            } else {
                console.log("Access denied: User is not an admin.");
                window.location.href = '/login';
            }
        } else {
            // Handle server errors (e.g., 404, 500)
            window.location.href = '/login';
        }

    } catch (error) {
        console.error("Error during admin check:", error);
        window.location.href = '/login';
    }
});