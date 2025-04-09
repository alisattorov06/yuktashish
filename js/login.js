document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kirilmoqda...';
            
            const credentials = {
                email: document.getElementById('login-email').value,
                password: document.getElementById('login-password').value
            };
            
            const response = await fetch('https://yuktashish.onrender.com/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Kirishda xatolik');
            }
            
            // Foydalanuvchi ma'lumotlarini saqlash
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Dashboard sahifasiga yo'naltirish
            window.location.href = 'dashboard.html';
            
        } catch (error) {
            console.error('Xatolik:', error);
            alert(error.message || 'Kirishda xatolik yuz berdi');
            
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Kirish';
        }
    });
});
