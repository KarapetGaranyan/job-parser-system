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
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayStats(data);

        } catch (error) {
            console.error('Ошибка загрузки статистики:', error);
            document.getElementById('statsContainer').innerHTML =
                `<div class="alert alert-danger">Ошибка загрузки: ${error.message}</div>`;
        }
    }

    displayStats(stats) {
        const container = document.getElementById('statsContainer');

        let html = `
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="card-title text-primary">${stats.total_vacancies}</h1>
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

        for (const [source, count] of Object.entries(stats.by_source)) {
            const percentage = stats.total_vacancies > 0 ? ((count / stats.total_vacancies) * 100).toFixed(1) : '0';
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>${source.toUpperCase()}</span>
                    <span class="badge bg-primary">${count} (${percentage}%)</span>
                </div>
            `;
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

        if (stats.top_companies.length > 0) {
            stats.top_companies.forEach(company => {
                html += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>${company.name}</span>
                        <span class="badge bg-success">${company.count}</span>
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

        if (stats.top_locations.length > 0) {
            stats.top_locations.forEach(location => {
                html += `
                    <div class="col-md-6 mb-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>${location.name}</span>
                            <span class="badge bg-info">${location.count}</span>
                        </div>
                    </div>
                `;
            });
        } else {
            html += '<div class="col-12"><p class="text-muted">Данные о локациях отсутствуют</p></div>';
        }

        html += `
                            </div>
                        </div>
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
