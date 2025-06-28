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
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3 class="mb-0">🔍 Поиск вакансий на HH.ru и SuperJob</h3>
                    </div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="mb-3">
                                <label for="vacancy" class="form-label">Название вакансии <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="vacancy" 
                                       placeholder="Например: Python разработчик" required>
                                <div class="form-text">
                                    Введите название профессии или ключевые слова для поиска
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="city" class="form-label">Город (необязательно)</label>
                                <input type="text" class="form-control" id="city" 
                                       placeholder="Например: Москва">
                            </div>
                            <div class="d-flex gap-2">
                                <button type="submit" class="btn btn-primary" id="searchBtn">
                                    <span id="spinner" class="spinner-border spinner-border-sm me-2" style="display: none;"></span>
                                    Найти вакансии
                                </button>
                                <button type="button" class="btn btn-danger" id="clearDbBtn">
                                    <span id="clearSpinner" class="spinner-border spinner-border-sm me-2" style="display: none;"></span>
                                    🗑️ Очистить БД
                                </button>
                            </div>
                        </form>

                        <div id="results" class="mt-4" style="display: none;">
                            <div id="searchStats" class="mb-3"></div>
                            <div id="vacanciesList"></div>
                            
                            <nav id="pagination" class="mt-4" style="display: none;">
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
    let allVacancies = [];
    let currentPage = 1;
    const itemsPerPage = 10;

    document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const vacancyInput = document.getElementById('vacancy');
    const citySelect = document.getElementById('city');
    const searchBtn = document.getElementById('searchBtn');
    const spinner = document.getElementById('spinner');
    const clearDbBtn = document.getElementById('clearDbBtn');  // ДОБАВЛЕНО
    const clearSpinner = document.getElementById('clearSpinner');  // ДОБАВЛЕНО
    const resultsDiv = document.getElementById('results');
    const searchStatsDiv = document.getElementById('searchStats');
    const vacanciesListDiv = document.getElementById('vacanciesList');
    const errorAlert = document.getElementById('errorAlert');

    // ДОБАВЛЕН ОБРАБОТЧИК ОЧИСТКИ БД
    clearDbBtn.addEventListener('click', async function() {
        // Подтверждение действия
        const confirmMessage = `⚠️ ВНИМАНИЕ! ⚠️

Вы уверены, что хотите удалить ВСЕ вакансии из базы данных?

Это действие:
- Удалит все сохраненные вакансии
- Нельзя будет отменить
- Очистит всю историю поиска

Продолжить?`;

        if (!confirm(confirmMessage)) {
            return;
        }

        // Показываем загрузку
        clearDbBtn.disabled = true;
        clearSpinner.style.display = 'inline-block';
        clearDbBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Очистка...';
        hideError();
        hideSuccess();

        try {
            console.log('🗑️ Начинаем очистку базы данных...');

            const response = await fetch('/api/clear-db', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ Результат очистки:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            // Показываем успешное сообщение
            const message = data.deleted_count > 0 
                ? `✅ База данных очищена! Удалено ${data.deleted_count} вакансий.`
                : '✅ База данных уже была пуста.';
            
            showSuccess(message);
            
            // Скрываем результаты поиска если они были
            resultsDiv.style.display = 'none';

        } catch (error) {
            console.error('❌ Ошибка очистки БД:', error);
            showError('Ошибка очистки базы данных: ' + error.message);
        } finally {
            clearDbBtn.disabled = false;
            clearSpinner.style.display = 'none';
            clearDbBtn.innerHTML = '🗑️ Очистить БД';
        }
    });

    // ОБРАБОТЧИК ФОРМЫ ПОИСКА (обновленный)
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const vacancy = vacancyInput.value.trim();
        const city = document.getElementById('city').value.trim();
        
        if (!vacancy) {
            showError('Введите название вакансии');
            return;
        }
        
        console.log('🔍 Поиск:', vacancy, city ? `в ${city}` : '(все города)');
        
        // Показываем загрузку
        searchBtn.disabled = true;
        spinner.style.display = 'inline-block';
        hideError();
        hideSuccess();
        resultsDiv.style.display = 'none';

        try {
            // Простое логирование
            console.log('🔍 Начинаем поиск:', vacancy, city ? `в городе: ${city}` : '(все города)');

            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    vacancy: vacancy,
                    city: city
                })
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            console.log('📊 Получены результаты:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            displayResults(data);

        } catch (error) {
            console.error('❌ Ошибка поиска:', error);
            showError('Ошибка поиска: ' + error.message);
        } finally {
            searchBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });

    
    // ФУНКЦИЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ
    // ФУНКЦИЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ
// ФУНКЦИЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ С ПАГИНАЦИЕЙ
function displayResults(data) {
    if (!data || !data.vacancies) {
        showError('Получены некорректные данные');
        return;
    }

    // Сохраняем все вакансии
    allVacancies = data.vacancies;
    currentPage = 1;  // Сброс на первую страницу

    const city = document.getElementById('city').value.trim();
    const cityInfo = city ? ` в ${city}` : ' (все города)';

    // Статистика
    let statsHtml = '<div class="row text-center mb-3">';
    
    statsHtml += `<div class="col-md-4">
        <div class="alert alert-primary mb-0">
            <strong>${data.total}</strong><br>
            Всего найдено${cityInfo}
        </div>
    </div>`;

    if (data.sources && data.sources.hh) {
        const hhStatus = data.sources.hh.status === 'success' ? 'success' : 'danger';
        statsHtml += `<div class="col-md-4">
            <div class="alert alert-${hhStatus} mb-0">
                <strong>${data.sources.hh.count}</strong><br>
                HH.ru${cityInfo}
            </div>
        </div>`;
    }

    if (data.sources && data.sources.superjob) {
        const sjStatus = data.sources.superjob.status === 'success' ? 'success' : 'danger';
        statsHtml += `<div class="col-md-4">
            <div class="alert alert-${sjStatus} mb-0">
                <strong>${data.sources.superjob.count}</strong><br>
                SuperJob${cityInfo}
            </div>
        </div>`;
    }

    statsHtml += '</div>';

    // Информация о городе
    if (city) {
        statsHtml += `<div class="alert alert-info">
            <strong>📍 Поиск в городе:</strong> ${city}
            <br><small>Чтобы искать по всем городам, оставьте поле города пустым</small>
        </div>`;
    }

    document.getElementById('searchStats').innerHTML = statsHtml;

    // Отображаем первую страницу
    displayPage(1);
    
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// ФУНКЦИЯ ОТОБРАЖЕНИЯ КОНКРЕТНОЙ СТРАНИЦЫ
function displayPage(page) {
    currentPage = page;
    
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageVacancies = allVacancies.slice(startIndex, endIndex);

    let vacanciesHtml = '';

    if (pageVacancies.length > 0) {
        pageVacancies.forEach(function(vacancy, index) {
            const globalIndex = startIndex + index + 1;  // Глобальный номер
            const title = vacancy.title || 'Не указано';
            const company = vacancy.company || 'Не указано';
            const salary = vacancy.salary || 'Не указана';
            const location = vacancy.location || 'Не указана';
            const link = vacancy.link || '#';
            let source = vacancy.source || 'unknown';

            // Проверка источника по ссылке
            if (source === 'unknown' && link) {
                if (link.includes('hh.ru')) source = 'hh';
                else if (link.includes('superjob.ru')) source = 'superjob';
            }

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
            } else {
                sourceClass = 'warning';
                sourceName = 'НЕИЗВЕСТНО';
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
                                    <strong>Зарплата:</strong> ${salary}<br>
                                    <strong>Местоположение:</strong> ${location}
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
        vacanciesHtml = '<div class="alert alert-warning">Вакансии не найдены</div>';
    }

    document.getElementById('vacanciesList').innerHTML = vacanciesHtml;
    updatePagination();
}

// ФУНКЦИЯ ОБНОВЛЕНИЯ ПАГИНАЦИИ
function updatePagination() {
    const totalPages = Math.ceil(allVacancies.length / itemsPerPage);
    const paginationNav = document.getElementById('pagination');
    const paginationList = document.getElementById('paginationList');
    const pageInfo = document.getElementById('pageInfo');

    if (totalPages <= 1) {
        paginationNav.style.display = 'none';
        return;
    }

    // Информация о странице
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, allVacancies.length);
    pageInfo.innerHTML = `Показано ${startItem}-${endItem} из ${allVacancies.length} вакансий`;

    // Кнопки пагинации
    let paginationHtml = '';

    // Кнопка "Предыдущая"
    if (currentPage > 1) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${currentPage - 1})">‹ Предыдущая</a>
            </li>
        `;
    }

    // Номера страниц (показываем максимум 5 страниц)
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage ? 'active' : '';
        paginationHtml += `
            <li class="page-item ${isActive}">
                <a class="page-link" href="#" onclick="goToPage(${i})">${i}</a>
            </li>
        `;
    }

    // Кнопка "Следующая"
    if (currentPage < totalPages) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${currentPage + 1})">Следующая ›</a>
            </li>
        `;
    }

    paginationList.innerHTML = paginationHtml;
    paginationNav.style.display = 'block';
}

// ФУНКЦИЯ ПЕРЕХОДА НА СТРАНИЦУ
window.goToPage = function(page) {
    if (page >= 1 && page <= Math.ceil(allVacancies.length / itemsPerPage)) {
        displayPage(page);
        document.getElementById('vacanciesList').scrollIntoView({ behavior: 'smooth' });
    }
}

    // ФУНКЦИЯ ДЛЯ ПОКАЗА УСПЕШНЫХ СООБЩЕНИЙ
    function showSuccess(message) {
        let successAlert = document.getElementById('successAlert');
        if (!successAlert) {
            successAlert = document.createElement('div');
            successAlert.id = 'successAlert';
            successAlert.className = 'alert alert-success mt-3';
            successAlert.style.display = 'none';
            errorAlert.parentNode.insertBefore(successAlert, errorAlert.nextSibling);
        }
        
        successAlert.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="hideSuccess()"></button>
            </div>
        `;
        successAlert.style.display = 'block';
        
        // Автоматически скрыть через 8 секунд
        setTimeout(() => {
            hideSuccess();
        }, 8000);
        
        successAlert.scrollIntoView({ behavior: 'smooth' });
    }

    // ФУНКЦИЯ ДЛЯ СКРЫТИЯ УСПЕШНЫХ СООБЩЕНИЙ
    window.hideSuccess = function() {
        const successAlert = document.getElementById('successAlert');
        if (successAlert) {
            successAlert.style.display = 'none';
        }
    }

    // ФУНКЦИЯ ДЛЯ ПОКАЗА ОШИБОК
    function showError(message) {
        errorAlert.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1"><strong>❌ Ошибка:</strong> ${message}</div>
                <button type="button" class="btn-close" onclick="hideError()"></button>
            </div>
        `;
        errorAlert.style.display = 'block';
        errorAlert.scrollIntoView({ behavior: 'smooth' });
    }

    // ФУНКЦИЯ ДЛЯ СКРЫТИЯ ОШИБОК
    window.hideError = function() {
        errorAlert.style.display = 'none';
    }

    // Проверяем API при загрузке
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            console.log('✅ API статус:', data);
            if (data.status === 'healthy') {
                console.log('🎉 Система готова к работе!');
            }
        })
        .catch(error => {
            console.error('❌ API недоступен:', error);
            showError('API сервера недоступен. Проверьте подключение к серверу.');
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
        'version': '2.0.0',
        'message': 'Job Parser System API работает',
        'parsers': ['hh', 'superjob']
    })


@app.route('/api/search', methods=['POST'])
def search_vacancies():
    """Поиск вакансий на всех платформах"""
    try:
        data = request.json
        query = data.get('vacancy', '').strip()
        city = data.get('city', '')

        if not query:
            return jsonify({'error': 'Не указано название вакансии'}), 400

        print(f"🔍 Начинаем поиск: {query}")

        results = {
            'query': query,
            'vacancies': [],
            'sources': {
                'hh': {'count': 0, 'status': 'pending'},
                'superjob': {'count': 0, 'status': 'pending'}
            },
            'total': 0
        }

        # Поиск на HH.ru
        try:
            print("📊 Парсинг HH.ru...")
            hh_vacancies = hh_parser.search(query, limit=50, city=city)
            results['vacancies'].extend(hh_vacancies)
            results['sources']['hh'] = {
                'count': len(hh_vacancies),
                'status': 'success'
            }
            print(f"✅ HH.ru: {len(hh_vacancies)} вакансий")
        except Exception as e:
            print(f"❌ Ошибка HH.ru: {e}")
            results['sources']['hh'] = {
                'count': 0,
                'status': 'error',
                'error': str(e)
            }

        # Поиск на SuperJob
        try:
            print("📊 Парсинг SuperJob...")
            sj_vacancies = sj_parser.search(query, limit=50,city=city)
            results['vacancies'].extend(sj_vacancies)
            results['sources']['superjob'] = {
                'count': len(sj_vacancies),
                'status': 'success'
            }
            print(f"✅ SuperJob: {len(sj_vacancies)} вакансий")
        except Exception as e:
            print(f"❌ Ошибка SuperJob: {e}")
            results['sources']['superjob'] = {
                'count': 0,
                'status': 'error',
                'error': str(e)
            }

        results['total'] = len(results['vacancies'])
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


@app.route('/api/clear-db', methods=['DELETE'])
def clear_database():
    """Полная очистка базы данных вакансий"""
    try:
        session = Session()

        # Подсчитываем количество записей до удаления
        count_before = session.query(Vacancy).count()

        # Удаляем все записи
        deleted_count = session.query(Vacancy).delete()
        session.commit()

        print(f"🗑️ База данных очищена! Удалено {deleted_count} вакансий")

        session.close()

        return jsonify({
            'success': True,
            'message': 'База данных успешно очищена',
            'deleted_count': deleted_count,
            'count_before': count_before
        })

    except Exception as e:
        print(f'💥 Ошибка очистки БД: {str(e)}')
        return jsonify({
            'error': f'Ошибка очистки базы данных: {str(e)}'
        }), 500


@app.route('/api/db-stats', methods=['GET'])
def get_db_stats():
    """Получение статистики базы данных"""
    try:
        session = Session()

        total_count = session.query(Vacancy).count()
        hh_count = session.query(Vacancy).filter_by(source='hh').count()
        sj_count = session.query(Vacancy).filter_by(source='superjob').count()

        session.close()

        return jsonify({
            'total_vacancies': total_count,
            'hh_vacancies': hh_count,
            'superjob_vacancies': sj_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Главная: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
