document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    const user = JSON.parse(localStorage.getItem('user'));
    const companyDashboard = document.getElementById('company-dashboard');
    const driverDashboard = document.getElementById('driver-dashboard');

    if (user?.role === 'company') {
        companyDashboard.style.display = 'block';
        loadCompanyCargos();
        document.getElementById('add-cargo-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const cargo = {
                direction: document.getElementById('cargo-direction').value,
                weight: document.getElementById('cargo-weight').value,
                volume: document.getElementById('cargo-volume').value,
                price: document.getElementById('cargo-price').value,
                phone: document.getElementById('cargo-phone').value,
                type: document.getElementById('cargo-type').value
            };
            fetch('http://localhost:5000/add-cargo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cargo)
            }).then(res => res.json()).then(data => {
                alert(data.message);
                loadCompanyCargos();
                e.target.reset();
            });
        });
    } else if (user?.role === 'driver') {
        driverDashboard.style.display = 'block';
        loadDriverCargos();
    }
});

function loadCompanyCargos() {
    fetch('http://localhost:5000/cargos')
        .then(res => res.json())
        .then(cargos => {
            const cargoList = document.getElementById('company-cargo-list');
            cargoList.innerHTML = '<h3>Aktiv yuklar</h3>';
            cargos.forEach((cargo, index) => {
                const card = document.createElement('div');
                card.classList.add('cargo-card');
                card.innerHTML = `
                    <div>
                        <p><i class="fa-solid fa-route"></i> ${cargo.direction}</p>
                        <p><i class="fa-solid fa-weight-hanging"></i> ${cargo.weight} kg</p>
                        <p><i class="fa-solid fa-box"></i> ${cargo.volume} m³</p>
                        <p><i class="fa-solid fa-truck"></i> Yukxona turi: ${cargo.type}</p>
                    </div>
                    <div>
                        <button onclick="editCargo(${cargo.id})"><i class="fa-solid fa-pen-to-square"></i></button>
                        <button onclick="deleteCargo(${cargo.id})"><i class="fa-solid fa-trash"></i></button>
                    </div>
                `;
                cargoList.appendChild(card);
            });
        });
}

function loadDriverCargos() {
    fetch('http://localhost:5000/cargos')
        .then(res => res.json())
        .then(cargos => {
            const cargoList = document.getElementById('driver-cargo-list');
            cargoList.innerHTML = '';
            cargos.forEach((cargo, index) => {
                const card = document.createElement('div');
                card.classList.add('cargo-card');
                card.innerHTML = `
                    <div>
                        <p><i class="fa-solid fa-route"></i> ${cargo.direction}</p>
                        <p><i class="fa-solid fa-weight-hanging"></i> ${cargo.weight} kg</p>
                        <p><i class="fa-solid fa-box"></i> ${cargo.volume} m³</p>
                        <p><i class="fa-solid fa-truck"></i> Yukxona turi: ${cargo.type}</p>
                    </div>
                    <button onclick="requestCargo(${cargo.id})"><i class="fa-solid fa-check-circle"></i> Qabul qilish</button>
                `;
                cargoList.appendChild(card);
            });
        });
}

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

function logout() {
    localStorage.removeItem('user');
    updateNav();
    window.location.href = 'index.html';
}