class VacanciesPage {
    constructor() {
        this.currentPage = 1;
        this.currentFilters = { source: '', company: '' };
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadVacancies();
    }

    bindEvents() {
        document.getElementById('sourceFilter').addEventListener('change', (e) => {
            this.currentFilters.source = e.target.value;
            this.currentPage = 1;
            this.loadVacancies();
        });

        const companyFilter = document.getElementById('companyFilter');
        let debounceTimer;
        companyFilter.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.currentFilters.company = e.target.value;
                this.currentPage = 1;
                this.loadVacancies();
            }, 500);
        });
    }

    async loadVacancies(page = 1) {
        try {
            const params = new URLSearchParams({
                page: page,
                per_page: 10,
                source: this.currentFilters.source,
                company: this.currentFilters.company
            });

            const response = await fetch(`/api/vacancies?${params}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayVacancies(data.vacancies);
            this.displayPagination(data.pagination);

        } catch (error) {
            console.error('Ошибка загрузки:', error);
            document.getElementById('vacanciesList').innerHTML =
                `<div class="alert alert-danger">Ошибка загрузки: ${error.message}</div>`;
        }
    }

    displayVacancies(vacancies) {
        const container = document.getElementById('vacanciesList');

        if (vacancies.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Вакансии не найдены</div>';
            return;
        }

        let html = '';
        vacancies.forEach(vacancy => {
            const sourceClass = vacancy.source === 'hh' ? 'success' : 'info';
            const date = vacancy.created_at ? new Date(vacancy.created_at).toLocaleDateString('ru-RU') : 'Не указано';

            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h5 class="card-title">${vacancy.title}</h5>
                                <p class="card-text">
                                    <strong>Компания:</strong> ${vacancy.company}<br>
                                    <strong>Зарплата:</strong> ${vacancy.salary}<br>
                                    <strong>Местоположение:</strong> ${vacancy.location || 'Не указано'}<br>
                                    <small class="text-muted">Добавлено: ${date}</small>
                                </p>
                            </div>
                            <div>
                                <span class="badge bg-${sourceClass}">${vacancy.source.toUpperCase()}</span>
                            </div>
                        </div>
                        <a href="${vacancy.link}" target="_blank" class="btn btn-outline-primary btn-sm">
                            🔗 Открыть вакансию
                        </a>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    displayPagination(pagination) {
        const nav = document.getElementById('pagination');

        if (pagination.pages <= 1) {
            nav.style.display = 'none';
            return;
        }

        let html = '<ul class="pagination justify-content-center">';

        // Предыдущая страница
        html += `<li class="page-item ${pagination.page <= 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="vacanciesPage.changePage(${pagination.page - 1})">Предыдущая</a>
        </li>`;

        // Номера страниц
        for (let i = 1; i <= pagination.pages; i++) {
            if (i === pagination.page) {
                html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                html += `<li class="page-item"><a class="page-link" href="#" onclick="vacanciesPage.changePage(${i})">${i}</a></li>`;
            }
        }

        // Следующая страница
        html += `<li class="page-item ${pagination.page >= pagination.pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="vacanciesPage.changePage(${pagination.page + 1})">Следующая</a>
        </li>`;

        html += '</ul>';
        nav.innerHTML = html;
        nav.style.display = 'block';
    }

    changePage(page) {
        this.currentPage = page;
        this.loadVacancies(page);
    }
}

// Инициализация
let vacanciesPage;
document.addEventListener('DOMContentLoaded', function() {
    vacanciesPage = new VacanciesPage();
});