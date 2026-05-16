// /static/Logout.js
// No imports needed — Clerk is already loaded globally from the <script> tag in your HTML

document.addEventListener('DOMContentLoaded', async () => {
  await window.Clerk.load();

  const btn = document.getElementById('sign-out');
  if (btn) {
    btn.addEventListener('click', async () => {
      await window.Clerk.signOut();
      window.location.href = '/login';
    });
  }
});