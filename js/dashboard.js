document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Avtorizatsiyani tekshirish
        const user = await checkAuth();
        if (!user) return;

        updateNav();
        
        // Foydalanuvchi ma'lumotlarini sozlash
        setupUserInfo(user);
        
        // Dashboardni sozlash
        if (user.role === 'company') {
            setupCompanyDashboard();
        } else if (user.role === 'driver') {
            setupDriverDashboard();
        }
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Dashboardni yuklashda xato yuz berdi');
        logout();
    }
});

// Avtorizatsiyani tekshirish funksiyasi
async function checkAuth() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        window.location.href = 'register.html';
        return null;
    }

    try {
        const response = await fetch('https://yuktashish.onrender.com/profile', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Avtorizatsiya amalga oshmadi');
        }
        
        return user;
    } catch (error) {
        console.error('Auth error:', error);
        logout();
        return null;
    }
}

// Foydalanuvchi ma'lumotlarini sozlash
function setupUserInfo(user) {
    const welcomeMessage = document.createElement('h2');
    welcomeMessage.textContent = `Xush kelibsiz, ${user.name}!`;
    welcomeMessage.style.marginBottom = '10px';
    
    const userRole = document.createElement('p');
    userRole.textContent = `Siz ${user.role === 'company' ? 'firma' : 'haydovchi'} sifatida kirdingiz`;
    userRole.style.color = '#666';
    
    const userInfoContainer = document.getElementById('user-info');
    userInfoContainer.innerHTML = '';
    userInfoContainer.appendChild(welcomeMessage);
    userInfoContainer.appendChild(userRole);
}

// Firma dashboardini sozlash
function setupCompanyDashboard() {
    const companyDashboard = document.getElementById('company-dashboard');
    companyDashboard.style.display = 'block';
    
    // Yuk qo'shish formasi
    document.getElementById('add-cargo-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const cargo = {
                direction: document.getElementById('cargo-direction').value,
                weight: parseFloat(document.getElementById('cargo-weight').value),
                volume: parseFloat(document.getElementById('cargo-volume').value),
                price: parseFloat(document.getElementById('cargo-price').value),
                phone: document.getElementById('cargo-phone').value,
                type: document.getElementById('cargo-type').value
            };
            
            const response = await fetch('https://yuktashish.onrender.com/add-cargo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cargo),
                credentials: 'include'
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Yuk qo\'shib bo\'lmadi');
            
            alert('Yuk muvaffaqiyatli qo\'shildi');
            e.target.reset();
            loadCompanyCargos();
        } catch (error) {
            console.error('Add cargo error:', error);
            alert('Xatolik: ' + error.message);
        }
    });
    
    loadCompanyCargos();
}

// Haydovchi dashboardini sozlash
function setupDriverDashboard() {
    const driverDashboard = document.getElementById('driver-dashboard');
    driverDashboard.style.display = 'block';
    
    // Haydovchi ma'lumotlarini yuklash (agar kerak bo'lsa)
    // ...
    
    loadDriverCargos();
}

// Firma yuklarini yuklash
async function loadCompanyCargos() {
    try {
        const response = await fetch('https://yuktashish.onrender.com/my-cargos', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Yuklarni yuklab bo\'lmadi');
        }
        
        const cargos = await response.json();
        displayCompanyCargos(cargos);
    } catch (error) {
        console.error('Load cargos error:', error);
        alert('Yuklarni yuklashda xato: ' + error.message);
    }
}

// Haydovchi yuklarini yuklash
async function loadDriverCargos() {
    try {
        const response = await fetch('https://yuktashish.onrender.com/cargos', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Yuklarni yuklab bo\'lmadi');
        }
        
        const cargos = await response.json();
        displayDriverCargos(cargos);
    } catch (error) {
        console.error('Load cargos error:', error);
        alert('Yuklarni yuklashda xato: ' + error.message);
    }
}

// Firma yuklarini ko'rsatish
function displayCompanyCargos(cargos) {
    const cargoList = document.getElementById('company-cargo-list');
    cargoList.innerHTML = '<h3><i class="fa-solid fa-truck-loading"></i> Mening yuklarim</h3>';
    
    if (!cargos || cargos.length === 0) {
        cargoList.innerHTML += '<p>Hozircha yuklar mavjud emas</p>';
        return;
    }
    
    cargos.forEach((cargo) => {
        const card = document.createElement('div');
        card.classList.add('cargo-card');
        card.innerHTML = `
            <div class="cargo-info">
                <p><i class="fa-solid fa-route"></i> ${cargo.direction}</p>
                <p><i class="fa-solid fa-weight-hanging"></i> ${cargo.weight} kg</p>
                <p><i class="fa-solid fa-box"></i> ${cargo.volume} m³</p>
                <p><i class="fa-solid fa-money-bill-wave"></i> ${cargo.price} so'm</p>
                <p><i class="fa-solid fa-phone"></i> ${cargo.phone}</p>
                <p><i class="fa-solid fa-truck"></i> ${cargo.type}</p>
            </div>
            <div class="cargo-actions">
                <button onclick="deleteCargo('${cargo.id}')"><i class="fa-solid fa-trash"></i> O'chirish</button>
            </div>
        `;
        cargoList.appendChild(card);
    });
}

// Haydovchi yuklarini ko'rsatish
function displayDriverCargos(cargos) {
    const cargoList = document.getElementById('driver-cargo-list');
    cargoList.innerHTML = '<h3><i class="fa-solid fa-boxes"></i> Mos keladigan yuklar</h3>';
    
    if (!cargos || cargos.length === 0) {
        cargoList.innerHTML += '<p>Hozircha mos yuklar mavjud emas</p>';
        return;
    }
    
    cargos.forEach((cargo) => {
        const card = document.createElement('div');
        card.classList.add('cargo-card');
        card.innerHTML = `
            <div class="cargo-info">
                <p><i class="fa-solid fa-route"></i> ${cargo.direction}</p>
                <p><i class="fa-solid fa-weight-hanging"></i> ${cargo.weight} kg</p>
                <p><i class="fa-solid fa-box"></i> ${cargo.volume} m³</p>
                <p><i class="fa-solid fa-money-bill-wave"></i> ${cargo.price} so'm</p>
                <p><i class="fa-solid fa-phone"></i> ${cargo.phone}</p>
                <p><i class="fa-solid fa-truck"></i> ${cargo.type}</p>
            </div>
            <div class="cargo-actions">
                <button onclick="requestCargo('${cargo.id}')"><i class="fa-solid fa-check-circle"></i> Qabul qilish</button>
            </div>
        `;
        cargoList.appendChild(card);
    });
}

// Yukni o'chirish
async function deleteCargo(cargoId) {
    if (!confirm('Haqiqatan ham bu yukni o\'chirmoqchimisiz?')) return;
    
    try {
        const response = await fetch(`https://yuktashish.onrender.com/cargos/${cargoId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Yukni o\'chirib bo\'lmadi');
        }
        
        alert('Yuk muvaffaqiyatli o\'chirildi');
        loadCompanyCargos();
    } catch (error) {
        console.error('Delete cargo error:', error);
        alert('Xatolik: ' + error.message);
    }
}

// Yukni qabul qilish
async function requestCargo(cargoId) {
    try {
        const response = await fetch(`https://yuktashish.onrender.com/cargos/${cargoId}/request`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Yukni qabul qilib bo\'lmadi');
        }
        
        alert('Yuk muvaffaqiyatli qabul qilindi!');
        loadDriverCargos();
    } catch (error) {
        console.error('Request cargo error:', error);
        alert('Xatolik: ' + error.message);
    }
}

// Navbarni yangilash
function updateNav() {
    const user = JSON.parse(localStorage.getItem('user'));
    const registerLink = document.getElementById('register-link');
    const logoutLink = document.getElementById('logout-link');

    if (user) {
        registerLink.style.display = 'none';
        logoutLink.style.display = 'block';
    } else {
        registerLink.style.display = 'block';
        logoutLink.style.display = 'none';
    }
}

// Tizimdan chiqish
async function logout() {
    try {
        await fetch('https://yuktashish.onrender.com/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}
