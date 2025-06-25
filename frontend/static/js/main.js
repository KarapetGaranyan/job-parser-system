// Check backend status
async function checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        document.getElementById('status').textContent =
            data.status === 'healthy' ? 'Система работает' : 'Ошибка подключения';
    } catch (error) {
        document.getElementById('status').textContent = 'Backend недоступен';
    }
}

// Check status on page load
document.addEventListener('DOMContentLoaded', checkBackendStatus);