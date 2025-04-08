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
        role: 'company'
    };
    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(company)
    }).then(res => res.json()).then(data => {
        alert(data.message);
        localStorage.setItem('user', JSON.stringify(company));
        window.location.href = 'dashboard.html';
    });
});

document.getElementById('driver-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const driver = {
        name: document.getElementById('driver-name').value,
        role: 'driver'
    };
    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(driver)
    }).then(res => res.json()).then(data => {
        alert(data.message);
        localStorage.setItem('user', JSON.stringify(driver));
        window.location.href = 'dashboard.html';
    });
});

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