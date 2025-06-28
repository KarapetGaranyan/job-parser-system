class StatsPage {
    constructor() {
        this.init();
    }

    init() {
        this.loadStats();
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayStats(data.stats || data); // Поддерживаем оба формата ответа

        } catch (error) {
            console.error('Ошибка загрузки статистики:', error);
            document.getElementById('statsContainer').innerHTML =
                `<div class="alert alert-danger">
                    <h6>❌ Ошибка загрузки статистики</h6>
                    <p>${error.message}</p>
                    <button class="btn btn-outline-danger btn-sm" onclick="statsPage.loadStats()">
                        🔄 Попробовать снова
                    </button>
                </div>`;
        }
    }

    displayStats(stats) {
        const container = document.getElementById('statsContainer');

        // Проверяем наличие данных
        if (!stats) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <h6>⚠️ Нет данных</h6>
                    <p>Статистика пока недоступна</p>
                </div>
            `;
            return;
        }

        // Безопасное извлечение данных с дефолтными значениями
        const totalVacancies = stats.total_vacancies || 0;
        const bySource = stats.by_source || {};
        const topCompanies = stats.top_companies || [];
        const topLocations = stats.top_locations || [];

        let html = `
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="card-title text-primary">${totalVacancies}</h1>
                            <p class="card-text">Всего вакансий в базе</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>📊 По источникам</h5>
                        </div>
                        <div class="card-body">
        `;

        // Статистика по источникам
        if (Object.keys(bySource).length > 0) {
            for (const [source, count] of Object.entries(bySource)) {
                const percentage = totalVacancies > 0 ? ((count / totalVacancies) * 100).toFixed(1) : '0';
                const sourceDisplayName = source === 'hh' ? 'HH.RU' :
                                        source === 'superjob' ? 'SUPERJOB' :
                                        source.toUpperCase();

                html += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>${sourceDisplayName}</span>
                        <span class="badge bg-primary">${count} (${percentage}%)</span>
                    </div>
                `;
            }
        } else {
            html += '<p class="text-muted">Данные по источникам отсутствуют</p>';
        }

        html += `
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>🏢 Топ компаний</h5>
                        </div>
                        <div class="card-body">
        `;

        // Топ компаний
        if (topCompanies.length > 0) {
            topCompanies.forEach(company => {
                const companyName = company.name || 'Не указано';
                const companyCount = company.count || 0;

                html += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-truncate" title="${companyName}">${companyName}</span>
                        <span class="badge bg-success">${companyCount}</span>
                    </div>
                `;
            });
        } else {
            html += '<p class="text-muted">Данные о компаниях отсутствуют</p>';
        }

        html += `
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>📍 Топ локации</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
        `;

        // Топ локации
        if (topLocations.length > 0) {
            topLocations.forEach(location => {
                const locationName = location.name || 'Не указано';
                const locationCount = location.count || 0;

                html += `
                    <div class="col-md-6 mb-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="text-truncate" title="${locationName}">${locationName}</span>
                            <span class="badge bg-info">${locationCount}</span>
                        </div>
                    </div>
                `;
            });
        } else {
            html += '<div class="col-12"><p class="text-muted">Данные о локациях отсутствуют</p></div>';
        }

        // Дополнительная статистика
        if (stats.time_stats) {
            const timeStats = stats.time_stats;
            html += `
                </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>⏰ Статистика по времени</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-md-4">
                                    <div class="bg-light p-3 rounded">
                                        <h4 class="text-primary">${timeStats.last_24_hours || 0}</h4>
                                        <small class="text-muted">За последние 24 часа</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="bg-light p-3 rounded">
                                        <h4 class="text-success">${timeStats.last_week || 0}</h4>
                                        <small class="text-muted">За последнюю неделю</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="bg-light p-3 rounded">
                                        <h4 class="text-info">${timeStats.last_month || 0}</h4>
                                        <small class="text-muted">За последний месяц</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `;
        } else {
            html += `
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }

        // Информация об обновлении
        const updateTime = new Date().toLocaleString('ru-RU');
        html += `
            <div class="row mt-3">
                <div class="col-12">
                    <div class="text-center text-muted">
                        <small>📊 Статистика обновлена: ${updateTime}</small>
                        <button class="btn btn-outline-primary btn-sm ms-2" onclick="statsPage.loadStats()">
                            🔄 Обновить
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }
}

// Инициализация
let statsPage;
document.addEventListener('DOMContentLoaded', function() {
    statsPage = new StatsPage();
});