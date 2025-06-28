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
        const sourceFilter = document.getElementById('sourceFilter');
        if (sourceFilter) {
            sourceFilter.addEventListener('change', (e) => {
                this.currentFilters.source = e.target.value;
                this.currentPage = 1;
                this.loadVacancies();
            });
        }

        const companyFilter = document.getElementById('companyFilter');
        if (companyFilter) {
            let debounceTimer;
            companyFilter.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.currentFilters.company = e.target.value.trim();
                    this.currentPage = 1;
                    this.loadVacancies();
                }, 500);
            });
        }
    }

    async loadVacancies(page = 1) {
        const container = document.getElementById('vacanciesList');

        // Показываем индикатор загрузки
        container.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <div class="mt-2">Загружаем вакансии...</div>
            </div>
        `;

        try {
            const params = new URLSearchParams({
                page: page.toString(),
                per_page: '10',
                source: this.currentFilters.source || '',
                company: this.currentFilters.company || ''
            });

            const response = await fetch(`/api/vacancies?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Проверяем структуру ответа
            if (!data.data && !data.vacancies) {
                throw new Error('Неверная структура ответа сервера');
            }

            // Поддерживаем разные форматы ответа
            const responseData = data.data || data;
            const vacancies = responseData.vacancies || [];
            const pagination = responseData.pagination || {};

            this.displayVacancies(vacancies);
            this.displayPagination(pagination);

        } catch (error) {
            console.error('Ошибка загрузки вакансий:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Ошибка загрузки вакансий</h6>
                    <p>${error.message}</p>
                    <button class="btn btn-outline-danger btn-sm" onclick="vacanciesPage.loadVacancies(${page})">
                        🔄 Попробовать снова
                    </button>
                </div>
            `;
        }
    }

    displayVacancies(vacancies) {
        const container = document.getElementById('vacanciesList');

        if (!Array.isArray(vacancies) || vacancies.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <h6>📭 Вакансии не найдены</h6>
                    <p>Попробуйте изменить фильтры поиска или очистить их</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="vacanciesPage.clearFilters()">
                        🔄 Очистить фильтры
                    </button>
                </div>
            `;
            return;
        }

        let html = '';
        vacancies.forEach(vacancy => {
            // Безопасное извлечение данных
            const title = vacancy.title || 'Не указано';
            const company = vacancy.company || 'Не указано';
            const salary = vacancy.salary || 'Не указана';
            const location = vacancy.location || 'Не указано';
            const link = vacancy.link || '#';
            const source = vacancy.source || 'unknown';

            // Определяем стиль для источника
            const sourceClass = source === 'hh' ? 'success' :
                               source === 'superjob' ? 'info' :
                               'secondary';
            const sourceName = source === 'hh' ? 'HH.RU' :
                              source === 'superjob' ? 'SUPERJOB' :
                              source.toUpperCase();

            // Форматируем дату
            let dateText = 'Не указано';
            if (vacancy.created_at) {
                try {
                    const date = new Date(vacancy.created_at);
                    if (!isNaN(date.getTime())) {
                        dateText = date.toLocaleDateString('ru-RU', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                } catch (e) {
                    console.warn('Ошибка парсинга даты:', vacancy.created_at);
                }
            }

            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    <span class="badge bg-${sourceClass}">${sourceName}</span>
                                    ${vacancy.id ? `<span class="badge bg-light text-dark ms-2">#${vacancy.id}</span>` : ''}
                                </div>
                                <h5 class="card-title">${title}</h5>
                                <p class="card-text">
                                    <strong>Компания:</strong> ${company}<br>
                                    <strong>Зарплата:</strong> ${salary}<br>
                                    <strong>Местоположение:</strong> ${location}<br>
                                    <small class="text-muted">Добавлено: ${dateText}</small>
                                </p>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <a href="${link}" target="_blank" class="btn btn-outline-primary btn-sm">
                                🔗 Открыть вакансию
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    displayPagination(pagination) {
        const nav = document.getElementById('pagination');

        if (!pagination || !nav) {
            if (nav) nav.style.display = 'none';
            return;
        }

        const { page = 1, pages = 1, total = 0 } = pagination;

        if (pages <= 1) {
            nav.style.display = 'none';
            return;
        }

        let html = '<ul class="pagination justify-content-center">';

        // Предыдущая страница
        html += `<li class="page-item ${page <= 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="vacanciesPage.changePage(${page - 1})" ${page <= 1 ? 'tabindex="-1"' : ''}>
                ‹ Предыдущая
            </a>
        </li>`;

        // Номера страниц (показываем максимум 5 страниц)
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(pages, page + 2);

        // Первая страница, если нужно
        if (startPage > 1) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="vacanciesPage.changePage(1)">1</a>
            </li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        // Основные страницы
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === page ? 'active' : ''}">
                ${i === page ?
                    `<span class="page-link">${i}</span>` :
                    `<a class="page-link" href="#" onclick="vacanciesPage.changePage(${i})">${i}</a>`
                }
            </li>`;
        }

        // Последняя страница, если нужно
        if (endPage < pages) {
            if (endPage < pages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="vacanciesPage.changePage(${pages})">${pages}</a>
            </li>`;
        }

        // Следующая страница
        html += `<li class="page-item ${page >= pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="vacanciesPage.changePage(${page + 1})" ${page >= pages ? 'tabindex="-1"' : ''}>
                Следующая ›
            </a>
        </li>`;

        html += '</ul>';

        // Информация о текущих результатах
        const startItem = ((page - 1) * 10) + 1;
        const endItem = Math.min(page * 10, total);
        html += `
            <div class="text-center mt-2 text-muted">
                <small>Показано ${startItem}-${endItem} из ${total} вакансий</small>
            </div>
        `;

        nav.innerHTML = html;
        nav.style.display = 'block';
    }

    changePage(page) {
        if (page < 1) return;

        this.currentPage = page;
        this.loadVacancies(page);

        // Прокручиваем к началу списка
        document.getElementById('vacanciesList').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    clearFilters() {
        // Сбрасываем фильтры
        this.currentFilters = { source: '', company: '' };
        this.currentPage = 1;

        // Очищаем поля фильтров
        const sourceFilter = document.getElementById('sourceFilter');
        const companyFilter = document.getElementById('companyFilter');

        if (sourceFilter) sourceFilter.value = '';
        if (companyFilter) companyFilter.value = '';

        // Перезагружаем данные
        this.loadVacancies(1);
    }
}

// Инициализация
let vacanciesPage;
document.addEventListener('DOMContentLoaded', function() {
    vacanciesPage = new VacanciesPage();
});