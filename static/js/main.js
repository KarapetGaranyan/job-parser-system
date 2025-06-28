class JobParserApp {
    constructor() {
        this.allVacancies = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkApiHealth();
    }

    bindEvents() {
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.handleSearch(e));
        }

        const clearDbBtn = document.getElementById('clearDbBtn');
        if (clearDbBtn) {
            clearDbBtn.addEventListener('click', () => this.handleClearDb());
        }
    }

    async handleSearch(e) {
        e.preventDefault();
        
        const vacancy = document.getElementById('vacancy').value.trim();
        const city = document.getElementById('city')?.value.trim() || '';

        if (!vacancy) {
            this.showError('Введите название вакансии');
            return;
        }

        this.showLoading(true);
        this.hideError();
        this.hideSuccess();

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vacancy, city })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            this.displayResults(data);

        } catch (error) {
            console.error('❌ Ошибка поиска:', error);
            this.showError('Ошибка поиска: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async handleClearDb() {
        if (!confirm('⚠️ Вы уверены, что хотите удалить ВСЕ вакансии из базы данных?')) {
            return;
        }

        this.showClearLoading(true);

        try {
            const response = await fetch('/api/clear-db', { method: 'DELETE' });
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            const message = data.deleted_count > 0 
                ? `✅ База данных очищена! Удалено ${data.deleted_count} вакансий.`
                : '✅ База данных уже была пуста.';

            this.showSuccess(message);
            this.hideResults();

        } catch (error) {
            console.error('❌ Ошибка очистки:', error);
            this.showError('Ошибка очистки: ' + error.message);
        } finally {
            this.showClearLoading(false);
        }
    }

    displayResults(data) {
        this.allVacancies = data.vacancies;
        this.currentPage = 1;

        this.displayStats(data);
        this.displayPage(1);
        this.showResults();
    }

    displayStats(data) {
        const city = document.getElementById('city')?.value.trim() || '';
        const cityInfo = city ? ` в ${city}` : ' (все города)';

        let statsHtml = '<div class="row text-center mb-3">';
        
        statsHtml += `<div class="col-md-4">
            <div class="alert alert-primary mb-0">
                <strong>${data.total}</strong><br>
                Всего найдено${cityInfo}
            </div>
        </div>`;

        if (data.sources?.hh) {
            const hhStatus = data.sources.hh.status === 'success' ? 'success' : 'danger';
            statsHtml += `<div class="col-md-4">
                <div class="alert alert-${hhStatus} mb-0">
                    <strong>${data.sources.hh.count}</strong><br>
                    HH.ru${cityInfo}
                </div>
            </div>`;
        }

        if (data.sources?.superjob) {
            const sjStatus = data.sources.superjob.status === 'success' ? 'success' : 'danger';
            statsHtml += `<div class="col-md-4">
                <div class="alert alert-${sjStatus} mb-0">
                    <strong>${data.sources.superjob.count}</strong><br>
                    SuperJob${cityInfo}
                </div>
            </div>`;
        }

        statsHtml += '</div>';

        document.getElementById('searchStats').innerHTML = statsHtml;
    }

    displayPage(page) {
        this.currentPage = page;
        
        const startIndex = (page - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageVacancies = this.allVacancies.slice(startIndex, endIndex);

        this.renderVacancies(pageVacancies, startIndex);
        this.updatePagination();
    }

    renderVacancies(vacancies, startIndex) {
        const container = document.getElementById('vacanciesList');
        
        if (vacancies.length === 0) {
            container.innerHTML = '<div class="alert alert-warning">Вакансии не найдены</div>';
            return;
        }

        let html = '';
        vacancies.forEach((vacancy, index) => {
            const globalIndex = startIndex + index + 1;
            html += this.createVacancyCard(vacancy, globalIndex);
        });

        container.innerHTML = html;
    }

    createVacancyCard(vacancy, index) {
        const { title, company, salary, location, link, source } = vacancy;
        
        let sourceClass = 'secondary';
        let sourceName = 'НЕИЗВЕСТНО';
        let cardClass = '';

        if (source === 'hh') {
            sourceClass = 'success';
            sourceName = 'HH.RU';
            cardClass = 'source-hh';
        } else if (source === 'superjob') {
            sourceClass = 'info';
            sourceName = 'SUPERJOB';
            cardClass = 'source-superjob';
        }

        return `
            <div class="card mb-3 ${cardClass}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center mb-2">
                                <span class="badge bg-light text-dark me-2">#${index}</span>
                                <span class="badge bg-${sourceClass}">${sourceName}</span>
                            </div>
                            <h5 class="card-title">${title || 'Не указано'}</h5>
                            <p class="card-text">
                                <strong>Компания:</strong> ${company || 'Не указано'}<br>
                                <strong>Зарплата:</strong> ${salary || 'Не указана'}<br>
                                <strong>Местоположение:</strong> ${location || 'Не указана'}
                            </p>
                        </div>
                    </div>
                    <a href="${link}" target="_blank" class="btn btn-outline-primary btn-sm">
                        🔗 Открыть вакансию
                    </a>
                </div>
            </div>
        `;
    }

    updatePagination() {
        const totalPages = Math.ceil(this.allVacancies.length / this.itemsPerPage);
        const paginationNav = document.getElementById('pagination');
        
        if (totalPages <= 1) {
            paginationNav.style.display = 'none';
            return;
        }

        const pageInfo = document.getElementById('pageInfo');
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, this.allVacancies.length);
        
        pageInfo.innerHTML = `Показано ${startItem}-${endItem} из ${this.allVacancies.length} вакансий`;

        this.renderPaginationButtons(totalPages);
        paginationNav.style.display = 'block';
    }

    renderPaginationButtons(totalPages) {
        const paginationList = document.getElementById('paginationList');
        let html = '';

        // Кнопка "Предыдущая"
        if (this.currentPage > 1) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.goToPage(${this.currentPage - 1})">‹ Предыдущая</a>
            </li>`;
        }

        // Номера страниц
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === this.currentPage ? 'active' : '';
            html += `<li class="page-item ${isActive}">
                <a class="page-link" href="#" onclick="app.goToPage(${i})">${i}</a>
            </li>`;
        }

        // Кнопка "Следующая"
        if (this.currentPage < totalPages) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.goToPage(${this.currentPage + 1})">Следующая ›</a>
            </li>`;
        }

        paginationList.innerHTML = html;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.allVacancies.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.displayPage(page);
            document.getElementById('vacanciesList').scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Утилиты для UI
    showLoading(show) {
        const btn = document.getElementById('searchBtn');
        const spinner = document.getElementById('spinner');
        
        if (show) {
            btn.disabled = true;
            spinner.style.display = 'inline-block';
        } else {
            btn.disabled = false;
            spinner.style.display = 'none';
        }
    }

    showClearLoading(show) {
    const btn = document.getElementById('clearDbBtn');
    const spinner = document.getElementById('clearSpinner');

    if (show) {
        btn.disabled = true;
        if (spinner) spinner.style.display = 'inline-block';
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Очистка...';
    } else {
        btn.disabled = false;
        if (spinner) spinner.style.display = 'none';
        btn.innerHTML = '🗑️ Очистить БД';
    }
}

    showError(message) {
        const alert = document.getElementById('errorAlert');
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1"><strong>❌ Ошибка:</strong> ${message}</div>
                <button type="button" class="btn-close" onclick="app.hideError()"></button>
            </div>
        `;
        alert.style.display = 'block';
        alert.scrollIntoView({ behavior: 'smooth' });
    }

    showSuccess(message) {
        let alert = document.getElementById('successAlert');
        if (!alert) {
            alert = document.createElement('div');
            alert.id = 'successAlert';
            alert.className = 'alert alert-success mt-3';
            document.getElementById('errorAlert').parentNode.insertBefore(alert, document.getElementById('errorAlert').nextSibling);
        }

        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="app.hideSuccess()"></button>
            </div>
        `;
        alert.style.display = 'block';

        setTimeout(() => this.hideSuccess(), 8000);
        alert.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        document.getElementById('errorAlert').style.display = 'none';
    }

    hideSuccess() {
        const alert = document.getElementById('successAlert');
        if (alert) alert.style.display = 'none';
    }

    showResults() {
        document.getElementById('results').style.display = 'block';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        document.getElementById('results').style.display = 'none';
    }

    async checkApiHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                console.log('🎉 Система готова к работе!');
            }
        } catch (error) {
            console.error('❌ API недоступен:', error);
            this.showError('API сервера недоступен. Проверьте подключение к серверу.');
        }
    }
}

// Инициализация приложения
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new JobParserApp();
});