main_js = '''// Основные JavaScript функции для Job Parser System

// Утилита для показа уведомлений
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';

    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Автоматически убираем через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce функция для поиска
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Проверка доступности API
async function checkAPIHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✅ API работает корректно');
            return true;
        }
    } catch (error) {
        console.error('❌ API недоступен:', error);
        showNotification('API сервер недоступен', 'danger');
        return false;
    }
}

// Проверяем API при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    checkAPIHealth();
});'''