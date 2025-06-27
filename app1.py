from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database.models import init_db, Vacancy, Session
from parsers.hh_parser import HHParser
from parsers.superjob_parser import SuperJobParser
from utils.export import ExportUtils
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Инициализация базы данных
init_db()

# Инициализация парсеров
hh_parser = HHParser()
sj_parser = SuperJobParser()
export_utils = ExportUtils()


@app.route('/')
def index():
    """Главная страница с формой поиска"""
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Parser System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .navbar-brand { font-weight: bold; }
        .source-hh { border-left: 4px solid #28a745; }
        .source-superjob { border-left: 4px solid #17a2b8; }
        .pagination-controls { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0; 
        }
        .search-controls { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
        }
        .progress-info {
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 0.9em;
        }
        .max-mode {
            border: 2px solid #dc3545;
            background: #fff5f5;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">🔍 Job Parser</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Поиск</a>
                <a class="nav-link" href="/api/vacancies">API</a>
                <a class="nav-link" href="/vacancies/text">Текст</a>
                <a class="nav-link" href="/export/csv">CSV</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card">
                    <div class="card-header">
                        <h3 class="mb-0">🔍 Поиск вакансий на HH.ru и SuperJob</h3>
                    </div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="vacancy" class="form-label">Название вакансии</label>
                                        <input type="text" class="form-control" id="vacancy" 
                                               placeholder="Например: Python разработчик" required>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-3">
                                        <label for="limitSelect" class="form-label">Количество вакансий</label>
                                        <select class="form-select" id="limitSelect">
                                            <option value="50">50 вакансий</option>
                                            <option value="100" selected>100 вакансий</option>
                                            <option value="200">200 вакансий</option>
                                            <option value="500">500 вакансий</option>
                                            <option value="1000">1000 вакансий</option>
                                            <option value="max">🚀 Максимум (все доступные)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-3">
                                        <label for="sourceSelect" class="form-label">Источники</label>
                                        <select class="form-select" id="sourceSelect">
                                            <option value="both">Все источники</option>
                                            <option value="hh">Только HH.ru</option>
                                            <option value="superjob">Только SuperJob</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div id="maxModeWarning" class="alert alert-warning max-mode" style="display: none;">
                                <h6>⚠️ Режим "Максимум"</h6>
                                <p class="mb-1">Будут найдены ВСЕ доступные вакансии. Это может занять несколько минут!</p>
                                <small>Рекомендуется для детального анализа рынка вакансий.</small>
                            </div>

                            <button type="submit" class="btn btn-primary btn-lg" id="searchBtn">
                                <span id="spinner" class="spinner-border spinner-border-sm me-2" style="display: none;"></span>
                                <span id="searchText">Найти вакансии</span>
                            </button>
                        </form>

                        <!-- Прогресс поиска -->
                        <div id="progressContainer" class="mt-3" style="display: none;">
                            <div class="progress-info" id="progressInfo">
                                Поиск запущен...
                            </div>
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     id="progressBar" role="progressbar" style="width: 0%"></div>
                            </div>
                        </div>

                        <div id="results" class="mt-4" style="display: none;">
                            <div id="searchStats" class="mb-3"></div>

                            <!-- Контролы пагинации -->
                            <div class="pagination-controls" id="paginationControls" style="display: none;">
                                <div class="row align-items-center">
                                    <div class="col-md-3">
                                        <label for="pageSize" class="form-label">На странице:</label>
                                        <select class="form-select" id="pageSize">
                                            <option value="10">10 вакансий</option>
                                            <option value="20" selected>20 вакансий</option>
                                            <option value="50">50 вакансий</option>
                                            <option value="100">100 вакансий</option>
                                        </select>
                                    </div>
                                    <div class="col-md-3">
                                        <label for="filterSource" class="form-label">Фильтр:</label>
                                        <select class="form-select" id="filterSource">
                                            <option value="">Все источники</option>
                                            <option value="hh">HH.ru</option>
                                            <option value="superjob">SuperJob</option>
                                        </select>
                                    </div>
                                    <div class="col-md-3">
                                        <label for="sortBy" class="form-label">Сортировка:</label>
                                        <select class="form-select" id="sortBy">
                                            <option value="default">По умолчанию</option>
                                            <option value="title">По названию</option>
                                            <option value="company">По компании</option>
                                            <option value="source">По источнику</option>
                                        </select>
                                    </div>
                                    <div class="col-md-3 text-end">
                                        <button class="btn btn-success" onclick="exportResults()">
                                            📥 Экспорт CSV
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Список вакансий -->
                            <div id="vacanciesList"></div>

                            <!-- Пагинация -->
                            <nav id="pagination" style="display: none;">
                                <div id="pageInfo" class="text-center mb-3 text-muted"></div>
                                <ul class="pagination justify-content-center" id="paginationList">
                                </ul>
                            </nav>
                        </div>

                        <div id="errorAlert" class="alert alert-danger mt-3" style="display: none;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    // Глобальные переменные
    let allVacancies = [];
    let filteredVacancies = [];
    let currentPage = 1;
    let currentPageSize = 20;
    let searchInProgress = false;

    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Инициализация приложения');

        // Обработчик изменения лимита
        document.getElementById('limitSelect').addEventListener('change', function() {
            const warning = document.getElementById('maxModeWarning');
            const searchText = document.getElementById('searchText');

            if (this.value === 'max') {
                warning.style.display = 'block';
                searchText.textContent = '🚀 Найти ВСЕ вакансии';
            } else {
                warning.style.display = 'none';
                searchText.textContent = 'Найти вакансии';
            }
        });

        // Обработчик отправки формы
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            if (searchInProgress) {
                console.log('🔄 Поиск уже выполняется');
                return;
            }

            const vacancy = document.getElementById('vacancy').value.trim();
            if (!vacancy) {
                showError('Введите название вакансии');
                return;
            }

            const limitValue = document.getElementById('limitSelect').value;
            const limit = limitValue === 'max' ? 10000 : parseInt(limitValue); // 10000 как "бесконечность"
            const sources = document.getElementById('sourceSelect').value;

            console.log('🔍 Начинаем поиск:', { vacancy, limit: limitValue, sources });

            searchInProgress = true;
            const searchBtn = document.getElementById('searchBtn');
            const spinner = document.getElementById('spinner');
            const progressContainer = document.getElementById('progressContainer');
            const progressInfo = document.getElementById('progressInfo');
            const progressBar = document.getElementById('progressBar');

            searchBtn.disabled = true;
            spinner.style.display = 'inline-block';
            progressContainer.style.display = 'block';
            progressBar.style.width = '10%';
            hideError();
            document.getElementById('results').style.display = 'none';

            if (limitValue === 'max') {
                progressInfo.innerHTML = '🚀 Режим "Максимум": Поиск всех доступных вакансий...<br><small>Это может занять 2-5 минут</small>';
            } else {
                progressInfo.innerHTML = `🔍 Поиск ${limit} вакансий...`;
            }

            try {
                // Создаем EventSource для получения прогресса (если поддерживается)
                let eventSource = null;
                let progressInterval = null;

                // Симулируем прогресс
                let progress = 10;
                progressInterval = setInterval(() => {
                    if (progress < 90) {
                        progress += Math.random() * 10;
                        progressBar.style.width = progress + '%';

                        if (progress < 30) {
                            progressInfo.innerHTML = '📊 Подключение к HH.ru...';
                        } else if (progress < 60) {
                            progressInfo.innerHTML = '🔍 Парсинг вакансий с HH.ru...';
                        } else {
                            progressInfo.innerHTML = '📋 Подключение к SuperJob...';
                        }
                    }
                }, 500);

                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        vacancy: vacancy,
                        limit: limit,
                        sources: sources,
                        unlimited: limitValue === 'max'
                    })
                });

                clearInterval(progressInterval);
                progressBar.style.width = '100%';
                progressInfo.innerHTML = '✅ Поиск завершен! Обработка результатов...';

                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }

                const data = await response.json();
                console.log('📊 Получены результаты:', data);

                if (data.error) {
                    throw new Error(data.error);
                }

                // Сохраняем результаты
                allVacancies = data.vacancies || [];
                console.log('💾 Сохранено вакансий:', allVacancies.length);

                // Применяем фильтры и отображаем
                applyFilters();
                displayResults(data);

            } catch (error) {
                console.error('❌ Ошибка поиска:', error);
                showError('Ошибка поиска: ' + error.message);
                progressInfo.innerHTML = '❌ Произошла ошибка при поиске';
                progressBar.classList.add('bg-danger');
            } finally {
                searchInProgress = false;
                searchBtn.disabled = false;
                spinner.style.display = 'none';

                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                    progressBar.classList.remove('bg-danger');
                }, 2000);
            }
        });

        // Обработчики для контролов пагинации
        document.getElementById('pageSize').addEventListener('change', function() {
            currentPageSize = parseInt(this.value);
            currentPage = 1;
            displayPage();
        });

        document.getElementById('filterSource').addEventListener('change', function() {
            applyFilters();
            currentPage = 1;
            displayPage();
        });

        document.getElementById('sortBy').addEventListener('change', function() {
            applySorting();
            displayPage();
        });

        // Функции для работы с данными
        function applyFilters() {
            const sourceFilter = document.getElementById('filterSource').value;

            filteredVacancies = allVacancies.filter(vacancy => {
                if (sourceFilter && vacancy.source !== sourceFilter) {
                    return false;
                }
                return true;
            });

            console.log('🔍 Применен фильтр:', sourceFilter, 'Результат:', filteredVacancies.length);
            applySorting();
        }

        function applySorting() {
            const sortValue = document.getElementById('sortBy').value;

            switch(sortValue) {
                case 'title':
                    filteredVacancies.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
                    break;
                case 'company':
                    filteredVacancies.sort((a, b) => (a.company || '').localeCompare(b.company || ''));
                    break;
                case 'source':
                    filteredVacancies.sort((a, b) => (a.source || '').localeCompare(b.source || ''));
                    break;
                default:
                    // По умолчанию не сортируем
                    break;
            }

            console.log('📊 Применена сортировка:', sortValue);
        }

        function displayResults(data) {
            // Показываем статистику
            let statsHtml = '<div class="row text-center mb-3">';

            // Основная статистика
            let totalClass = 'primary';
            let totalText = `${data.total} найдено`;

            if (data.total >= 1000) {
                totalClass = 'success';
                totalText = `🎉 ${data.total} найдено!`;
            } else if (data.total >= 500) {
                totalClass = 'info';
                totalText = `✨ ${data.total} найдено`;
            }

            statsHtml += `<div class="col-md-4">
                <div class="alert alert-${totalClass} mb-0">
                    <strong>${totalText}</strong><br>Всего вакансий
                </div>
            </div>`;

            if (data.sources && data.sources.hh) {
                const hhStatus = data.sources.hh.status === 'success' ? 'success' : 'danger';
                statsHtml += `<div class="col-md-4">
                    <div class="alert alert-${hhStatus} mb-0">
                        <strong>${data.sources.hh.count}</strong><br>HH.ru
                        ${data.sources.hh.pages ? `<br><small>${data.sources.hh.pages} страниц</small>` : ''}
                    </div>
                </div>`;
            }

            if (data.sources && data.sources.superjob) {
                const sjStatus = data.sources.superjob.status === 'success' ? 'success' : 'danger';
                statsHtml += `<div class="col-md-4">
                    <div class="alert alert-${sjStatus} mb-0">
                        <strong>${data.sources.superjob.count}</strong><br>SuperJob
                        ${data.sources.superjob.pages ? `<br><small>${data.sources.superjob.pages} страниц</small>` : ''}
                    </div>
                </div>`;
            }

            statsHtml += '</div>';

            // Дополнительная информация для больших результатов
            if (data.total >= 100) {
                statsHtml += `<div class="alert alert-info">
                    <strong>📈 Отличный результат!</strong> 
                    Найдено ${data.total} вакансий. Используйте фильтры и сортировку для анализа.
                    ${data.total >= 500 ? '<br><strong>💡 Совет:</strong> Такое количество вакансий идеально для анализа рынка труда!' : ''}
                </div>`;
            }

            document.getElementById('searchStats').innerHTML = statsHtml;

            if (filteredVacancies.length > 0) {
                document.getElementById('paginationControls').style.display = 'block';
                currentPage = 1;
                displayPage();
            } else {
                document.getElementById('vacanciesList').innerHTML = '<div class="alert alert-warning">Вакансии не найдены</div>';
                document.getElementById('pagination').style.display = 'none';
                document.getElementById('paginationControls').style.display = 'none';
            }

            document.getElementById('results').style.display = 'block';
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }

        function displayPage() {
            const startIndex = (currentPage - 1) * currentPageSize;
            const endIndex = startIndex + currentPageSize;
            const pageVacancies = filteredVacancies.slice(startIndex, endIndex);

            let vacanciesHtml = '';

            if (pageVacancies.length > 0) {
                pageVacancies.forEach(function(vacancy, index) {
                    const globalIndex = startIndex + index + 1;
                    const title = vacancy.title || 'Не указано';
                    const company = vacancy.company || 'Не указано';
                    const salary = vacancy.salary || 'Не указана';
                    const location = vacancy.location || '';
                    const link = vacancy.link || '#';
                    const source = vacancy.source || 'unknown';

                    let sourceClass = 'secondary';
                    let sourceName = 'UNKNOWN';
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

                    vacanciesHtml += `
                        <div class="card mb-3 ${cardClass}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <div class="d-flex align-items-center mb-2">
                                            <span class="badge bg-light text-dark me-2">#${globalIndex}</span>
                                            <span class="badge bg-${sourceClass}">${sourceName}</span>
                                        </div>
                                        <h5 class="card-title">${title}</h5>
                                        <p class="card-text">
                                            <strong>Компания:</strong> ${company}<br>
                                            <strong>Зарплата:</strong> ${salary}
                                            ${location ? `<br><strong>Местоположение:</strong> ${location}` : ''}
                                        </p>
                                    </div>
                                </div>
                                <a href="${link}" target="_blank" class="btn btn-outline-primary btn-sm">
                                    🔗 Открыть вакансию
                                </a>
                            </div>
                        </div>
                    `;
                });
            } else {
                vacanciesHtml = '<div class="alert alert-warning">Вакансии не найдены с выбранными фильтрами</div>';
            }

            document.getElementById('vacanciesList').innerHTML = vacanciesHtml;
            updatePagination();
        }

        function updatePagination() {
            const totalPages = Math.ceil(filteredVacancies.length / currentPageSize);

            // Информация о странице
            const startItem = (currentPage - 1) * currentPageSize + 1;
            const endItem = Math.min(currentPage * currentPageSize, filteredVacancies.length);
            document.getElementById('pageInfo').innerHTML = 
                `Показано ${startItem}-${endItem} из ${filteredVacancies.length} вакансий`;

            if (totalPages <= 1) {
                document.getElementById('pagination').style.display = 'none';
                return;
            }

            let paginationHtml = '';

            // Кнопка "Предыдущая"
            paginationHtml += `
                <li class="page-item ${currentPage <= 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${currentPage - 1})" ${currentPage <= 1 ? 'tabindex="-1"' : ''}>
                        &laquo; Предыдущая
                    </a>
                </li>
            `;

            // Номера страниц
            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);

            if (startPage > 1) {
                paginationHtml += `<li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(1)">1</a>
                </li>`;
                if (startPage > 2) {
                    paginationHtml += `<li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>`;
                }
            }

            for (let i = startPage; i <= endPage; i++) {
                paginationHtml += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                    </li>
                `;
            }

            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    paginationHtml += `<li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>`;
                }
                paginationHtml += `<li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${totalPages})">${totalPages}</a>
                </li>`;
            }

            // Кнопка "Следующая"
            paginationHtml += `
                <li class="page-item ${currentPage >= totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${currentPage + 1})" ${currentPage >= totalPages ? 'tabindex="-1"' : ''}>
                        Следующая &raquo;
                    </a>
                </li>
            `;

            document.getElementById('paginationList').innerHTML = paginationHtml;
            document.getElementById('pagination').style.display = 'block';
        }

        // Глобальные функции
        window.changePage = function(page) {
            const totalPages = Math.ceil(filteredVacancies.length / currentPageSize);

            if (page >= 1 && page <= totalPages && page !== currentPage) {
                currentPage = page;
                displayPage();
                document.getElementById('vacanciesList').scrollIntoView({ behavior: 'smooth' });
            }
        };

        window.exportResults = function() {
            if (filteredVacancies.length === 0) {
                showError('Нет данных для экспорта');
                return;
            }

            try {
                const csvContent = generateCSV(filteredVacancies);
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `vacancies_${new Date().toISOString().split('T')[0]}.csv`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                console.log('✅ Экспорт завершен');
            } catch (error) {
                console.error('❌ Ошибка экспорта:', error);
                showError('Ошибка экспорта: ' + error.message);
            }
        };

        function generateCSV(vacancies) {
            const headers = ['№', 'Название', 'Компания', 'Зарплата', 'Местоположение', 'Источник', 'Ссылка'];
            let csv = '\uFEFF' + headers.join(';') + '\n';

            vacancies.forEach((vacancy, index) => {
                const row = [
                    index + 1,
                    `"${(vacancy.title || '').replace(/"/g, '""')}"`,
                    `"${(vacancy.company || '').replace(/"/g, '""')}"`,
                    `"${(vacancy.salary || '').replace(/"/g, '""')}"`,
                    `"${(vacancy.location || '').replace(/"/g, '""')}"`,
                    (vacancy.source || 'unknown').toUpperCase(),
                    vacancy.link || ''
                ];
                csv += row.join(';') + '\n';
            });

            return csv;
        }

        function showError(message) {
            const errorAlert = document.getElementById('errorAlert');
            errorAlert.textContent = message;
            errorAlert.style.display = 'block';
            errorAlert.scrollIntoView({ behavior: 'smooth' });
        }

        function hideError() {
            document.getElementById('errorAlert').style.display = 'none';
        }

        // Проверяем API при загрузке
        fetch('/api/health')
            .then(response => response.json())
            .then(data => console.log('✅ API статус:', data))
            .catch(error => {
                console.error('❌ API недоступен:', error);
                showError('API сервера недоступен. Проверьте подключение.');
            });
    });
    </script>
</body>
</html>
    """
    return html


@app.route('/api/health')
def health():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0',
        'message': 'Job Parser System API работает',
        'parsers': ['hh', 'superjob'],
        'features': ['unlimited_search', 'pagination', 'filters', 'export']
    })


@app.route('/api/search', methods=['POST'])
def search_vacancies():
    """Поиск вакансий на всех платформах без ограничений"""
    try:
        data = request.json
        query = data.get('vacancy', '').strip()
        limit = data.get('limit', 100)
        sources = data.get('sources', 'both')
        unlimited = data.get('unlimited', False)

        if not query:
            return jsonify({'error': 'Не указано название вакансии'}), 400

        # Если режим "максимум", устанавливаем очень большой лимит
        if unlimited:
            limit = 10000  # Практически без ограничений
            print(f"🚀 РЕЖИМ МАКСИМУМ: Поиск всех доступных вакансий по запросу '{query}'")
        else:
            print(f"🔍 Начинаем поиск: {query} (лимит: {limit}, источники: {sources})")

        results = {
            'query': query,
            'vacancies': [],
            'sources': {
                'hh': {'count': 0, 'status': 'pending', 'pages': 0},
                'superjob': {'count': 0, 'status': 'pending', 'pages': 0}
            },
            'total': 0,
            'limit': limit,
            'unlimited': unlimited
        }

        # Распределяем лимит между источниками
        if sources == 'both':
            hh_limit = limit // 2 if not unlimited else 5000
            sj_limit = limit - hh_limit if not unlimited else 5000
        elif sources == 'hh':
            hh_limit = limit
            sj_limit = 0
        elif sources == 'superjob':
            hh_limit = 0
            sj_limit = limit
        else:
            hh_limit = limit // 2 if not unlimited else 5000
            sj_limit = limit - hh_limit if not unlimited else 5000

        # Поиск на HH.ru
        if hh_limit > 0:
            try:
                print(f"📊 Парсинг HH.ru (лимит: {'БЕЗ ОГРАНИЧЕНИЙ' if unlimited else hh_limit})...")
                hh_vacancies = hh_parser.search(query, limit=hh_limit)
                results['vacancies'].extend(hh_vacancies)

                # Подсчитываем примерное количество страниц
                pages_hh = len(hh_vacancies) // 50 + 1 if len(hh_vacancies) > 0 else 0

                results['sources']['hh'] = {
                    'count': len(hh_vacancies),
                    'status': 'success',
                    'pages': pages_hh
                }
                print(f"✅ HH.ru: {len(hh_vacancies)} вакансий ({pages_hh} страниц)")
            except Exception as e:
                print(f"❌ Ошибка HH.ru: {e}")
                results['sources']['hh'] = {
                    'count': 0,
                    'status': 'error',
                    'error': str(e),
                    'pages': 0
                }

        # Поиск на SuperJob
        if sj_limit > 0:
            try:
                print(f"📊 Парсинг SuperJob (лимит: {'БЕЗ ОГРАНИЧЕНИЙ' if unlimited else sj_limit})...")
                sj_vacancies = sj_parser.search(query, limit=sj_limit)
                results['vacancies'].extend(sj_vacancies)

                # Подсчитываем примерное количество страниц
                pages_sj = len(sj_vacancies) // 20 + 1 if len(sj_vacancies) > 0 else 0

                results['sources']['superjob'] = {
                    'count': len(sj_vacancies),
                    'status': 'success',
                    'pages': pages_sj
                }
                print(f"✅ SuperJob: {len(sj_vacancies)} вакансий ({pages_sj} страниц)")
            except Exception as e:
                print(f"❌ Ошибка SuperJob: {e}")
                results['sources']['superjob'] = {
                    'count': 0,
                    'status': 'error',
                    'error': str(e),
                    'pages': 0
                }

        results['total'] = len(results['vacancies'])

        if unlimited:
            print(f"🎉 МАКСИМАЛЬНЫЙ ПОИСК ЗАВЕРШЕН! Найдено {results['total']} вакансий")
        else:
            print(f"🎉 Поиск завершен. Всего: {results['total']} вакансий")

        return jsonify(results)

    except Exception as e:
        print('💥 Ошибка в search_vacancies:', traceback.format_exc())
        return jsonify({'error': f'Ошибка на сервере: {str(e)}'}), 500


@app.route('/api/vacancies', methods=['GET'])
def get_all_vacancies():
    """Получение всех вакансий из базы данных"""
    try:
        session = Session()
        vacancies = session.query(Vacancy).all()

        result = {
            'vacancies': [],
            'total': len(vacancies)
        }

        for v in vacancies:
            result['vacancies'].append({
                'id': v.id,
                'title': v.title,
                'link': v.link,
                'company': v.company,
                'salary': v.salary,
                'location': getattr(v, 'location', ''),
                'source': v.source
            })

        session.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vacancies/text')
def vacancies_text():
    """Текстовое представление всех вакансий"""
    try:
        session = Session()
        vacancies = session.query(Vacancy).all()

        text_data = export_utils.to_text(vacancies)
        session.close()

        return f'<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px;">{text_data}</pre>'

    except Exception as e:
        return f'<pre>Ошибка: {str(e)}</pre>'


@app.route('/export/csv')
def export_csv():
    """Экспорт всех вакансий в CSV"""
    try:
        session = Session()
        vacancies = session.query(Vacancy).all()
        csv_data = export_utils.to_csv(vacancies)
        session.close()

        return Response(
            csv_data,
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment;filename=vacancies.csv'}
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Запуск Job Parser System v3.0 - UNLIMITED EDITION")
    print("=" * 60)
    print("🌐 Главная: http://localhost:5000")
    print("📊 API: http://localhost:5000/api/health")
    print("📋 Текст: http://localhost:5000/vacancies/text")
    print("📥 CSV: http://localhost:5000/export/csv")
    print("=" * 60)
    print("📡 Парсеры: HH.ru + SuperJob")
    print("💾 База данных: SQLite")
    print("")
    print("✨ НОВЫЕ ВОЗМОЖНОСТИ v3.0:")
    print("   🚀 БЕЗ ОГРАНИЧЕНИЙ на количество вакансий")
    print("   📊 Режим 'Максимум' - ВСЕ доступные вакансии")
    print("   🔄 Динамическая пагинация")
    print("   📈 Прогресс-бар поиска")
    print("   🎯 Умные фильтры и сортировка")
    print("   📥 Экспорт больших объемов данных")
    print("   📋 Подробная статистика по страницам")
    print("")
    print("⚠️  ВНИМАНИЕ: Режим 'Максимум' может занять несколько минут!")
    print("✅ Готов к работе!")

    app.run(host='0.0.0.0', port=5000, debug=True)