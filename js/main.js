document.addEventListener('DOMContentLoaded', () => {
    const cargoList = document.getElementById('cargo-list');
    const cargos = JSON.parse(localStorage.getItem('cargos')) || [];

    const renderCargos = (filteredCargos) => {
        cargoList.innerHTML = '';
        filteredCargos.forEach((cargo, index) => {
            const card = document.createElement('div');
            card.classList.add('cargo-card');
            card.style.animationDelay = `${index * 0.1}s`;
            card.innerHTML = `
                <div>
                    <p><i class="fa-solid fa-route"></i> ${cargo.direction}</p>
                    <p><i class="fa-solid fa-weight-hanging"></i> ${cargo.weight} kg</p>
                    <p><i class="fa-solid fa-box"></i> ${cargo.volume} m³</p>
                    <p><i class="fa-solid fa-phone"></i> ${cargo.phone}</p>
                    <p><i class="fa-solid fa-money-bill-wave"></i> ${cargo.price} so'm</p>
                </div>
                <button onclick="requestCargo(${index})"><i class="fa-solid fa-check-circle"></i> Qabul qilish</button>
            `;
            cargoList.appendChild(card);
        });
    };

    renderCargos(cargos);

    document.querySelectorAll('.filters select, .filters input').forEach(input => {
        input.addEventListener('change', () => {
            const type = document.getElementById('cargo-type').value;
            const region = document.getElementById('region').value;
            const weight = document.getElementById('weight').value;

            const filtered = cargos.filter(cargo => {
                return (!type || cargo.type === type) &&
                       (!region || cargo.direction.includes(region)) &&
                       (!weight || cargo.weight <= weight);
            });
            cargoList.style.opacity = '0';
            setTimeout(() => {
                renderCargos(filtered);
                cargoList.style.opacity = '1';
            }, 300);
        });
    });

    window.addEventListener('scroll', () => {
        document.querySelectorAll('.cargo-card').forEach(card => {
            const rect = card.getBoundingClientRect();
            if (rect.top < window.innerHeight - 100) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    });
});

function requestCargo(index) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || user.role !== 'driver') {
        alert('Faqat haydovchilar yuk qabul qilishi mumkin!');
        return;
    }

    let cargos = JSON.parse(localStorage.getItem('cargos')) || [];
    const cargo = cargos[index];
    const request = {
        cargoIndex: index,
        cargo: cargo,
        driver: user,
        status: 'pending' // Tasdiqlanishni kutmoqda
    };

    let requests = JSON.parse(localStorage.getItem('requests')) || [];
    requests.push(request);
    localStorage.setItem('requests', JSON.stringify(requests));

    const card = document.querySelectorAll('.cargo-card')[index];
    card.style.transform = 'translateX(100%)';
    card.style.opacity = '0';
    setTimeout(() => {
        alert('Yuk qabul qilish so‘rovi firmaga jo‘natildi!');
    }, 500);
}