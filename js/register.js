document.addEventListener('DOMContentLoaded', () => {
    showTab('company');
    
    // Firma ro'yxatdan o'tish
    document.getElementById('company-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const company = {
            name: document.getElementById('company-name').value,
            email: document.getElementById('company-email').value,
            password: document.getElementById('company-password').value,
            phone: document.getElementById('company-phone').value,
            role: 'company',
            company_name: document.getElementById('company-name').value
        };
        
        await registerUser(company);
    });
    
    // Haydovchi ro'yxatdan o'tish
    document.getElementById('driver-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const driver = {
            name: document.getElementById('driver-name').value,
            email: document.getElementById('driver-email').value,
            password: document.getElementById('driver-password').value,
            phone: document.getElementById('driver-phone').value,
            role: 'driver',
            vehicle_type: document.getElementById('driver-vehicle-type').value
        };
        
        await registerUser(driver);
    });
});

async function registerUser(userData) {
    try {
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Jo\'natilmoqda...';
        
        const response = await fetch('https://yuktashish.onrender.com/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Ro\'yxatdan o\'tishda xatolik');
        }
        
        alert('Ro\'yxatdan o\'tish muvaffaqiyatli! Iltimos, tizimga kiring.');
        window.location.href = 'login.html';
        
    } catch (error) {
        console.error('Xatolik:', error);
        alert(error.message || 'Ro\'yxatdan o\'tishda xatolik yuz berdi');
        
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Ro\'yxatdan o\'tish';
    }
}

function showTab(tab) {
    document.querySelectorAll('.register-form').forEach(form => {
        form.style.display = 'none';
    });
    
    document.getElementById(`${tab}-form`).style.display = 'flex';
    
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelector(`button[onclick="showTab('${tab}')"]`).classList.add('active');
}
