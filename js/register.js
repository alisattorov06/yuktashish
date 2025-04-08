document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    showTab('company');
});

function showTab(tab) {
    const tabs = document.querySelectorAll('.tab');
    const forms = document.querySelectorAll('.register-form');

    tabs.forEach(btn => btn.classList.remove('active'));
    const clickedTab = document.querySelector(`button[onclick="showTab('${tab}')"]`);
    if (clickedTab) clickedTab.classList.add('active');

    forms.forEach(form => {
        form.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        form.style.opacity = '0';
        form.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            if (form.id !== `${tab}-form`) form.style.display = 'none';
        }, 300);
    });

    const activeForm = document.getElementById(`${tab}-form`);
    if (activeForm) {
        activeForm.style.display = 'flex';
        setTimeout(() => {
            activeForm.style.opacity = '1';
            activeForm.style.transform = 'translateX(0)';
        }, 10);
    }
}

document.getElementById('company-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const company = {
        name: document.getElementById('company-name').value,
        email: document.getElementById('company-email').value,
        password: document.getElementById('company-password').value,
        role: 'company',
        tin: document.getElementById('company-tin').value,
        phone: document.getElementById('company-phone').value,
        address: document.getElementById('company-address').value
    };
    
    registerUser(company);
});

document.getElementById('driver-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const driver = {
        name: document.getElementById('driver-name').value,
        email: document.getElementById('driver-email').value,
        password: document.getElementById('driver-password').value,
        role: 'driver',
        cargoType: document.getElementById('driver-cargo-type').value,
        maxWeight: document.getElementById('driver-weight').value,
        maxVolume: document.getElementById('driver-volume').value,
        plateNumber: document.getElementById('driver-plate').value
    };
    
    registerUser(driver);
});

async function registerUser(userData) {
    try {
        const response = await fetch('https://yuktashish.onrender.com/register', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(userData),
            credentials: 'include' // Sessiya cookie'larini saqlash uchun
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Ro\'yxatdan o\'tishda xato yuz berdi');
        }

        // LocalStorage ga faqat zarur ma'lumotlarni saqlash
        localStorage.setItem('user', JSON.stringify({
            id: data.user_id,
            name: userData.name,
            role: userData.role,
            email: userData.email
        }));
        
        // Dashboard sahifasiga yo'naltirish
        window.location.href = 'dashboard.html';
        
    } catch (err) {
        console.error('Xatolik:', err);
        alert(err.message);
    }
}

function updateNav() {
    const user = JSON.parse(localStorage.getItem('user'));
    const registerLink = document.getElementById('register-link');
    const logoutLink = document.getElementById('logout-link');

    if (user) {
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        if (registerLink) registerLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('user');
    // Backenddan chiqish uchun so'rov yuborish
    fetch('https://yuktashish.onrender.com/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(() => {
        updateNav();
        window.location.href = 'index.html';
    })
    .catch(err => console.error('Chiqishda xato:', err));
}
