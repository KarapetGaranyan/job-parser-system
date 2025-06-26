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
                                <label for="vacancy" class="form-label">Название вакансии</label>
                                <input type="text" class="form-control" id="vacancy" 
                                       placeholder="Например: Python разработчик" required>
                            </div>
                            <button type="submit" class="btn btn-primary" id="searchBtn">
                                <span id="spinner" class="spinner-border spinner-border-sm me-2" style="display: none;"></span>
                                Найти вакансии
                            </button>
                        </form>

                        <div id="results" class="mt-4" style="display: none;">
                            <div id="searchStats" class="mb-3"></div>
                            <div id="vacanciesList"></div>
                        </div>

                        <div id="errorAlert" class="alert alert-danger mt-3" style="display: none;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const searchForm = document.getElementById('searchForm');
        const vacancyInput = document.getElementById('vacancy');
        const searchBtn = document.getElementById('searchBtn');
        const spinner = document.getElementById('spinner');
        const resultsDiv = document.getElementById('results');
        const searchStatsDiv = document.getElementById('searchStats');
        const vacanciesListDiv = document.getElementById('vacanciesList');
        const errorAlert = document.getElementById('errorAlert');

        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const vacancy = vacancyInput.value.trim();
            if (!vacancy) {
                showError('Введите название вакансии');
                return;
            }

            // Показываем загрузку
            searchBtn.disabled = true;
            spinner.style.display = 'inline-block';
            hideError();
            resultsDiv.style.display = 'none';

            try {
                console.log('🔍 Начинаем поиск:', vacancy);

                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ vacancy: vacancy })
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

        function displayResults(data) {
            if (!data || !data.vacancies) {
                showError('Получены некорректные данные');
                return;
            }

            // Статистика
            let statsHtml = '<div class="row text-center mb-3">';
            statsHtml += `<div class="col-md-4"><div class="alert alert-primary mb-0"><strong>${data.total}</strong><br>Всего найдено</div></div>`;

            if (data.sources.hh) {
                const hhStatus = data.sources.hh.status === 'success' ? 'success' : 'danger';
                statsHtml += `<div class="col-md-4"><div class="alert alert-${hhStatus} mb-0"><strong>${data.sources.hh.count}</strong><br>HH.ru</div></div>`;
            }

            if (data.sources.superjob) {
                const sjStatus = data.sources.superjob.status === 'success' ? 'success' : 'danger';
                statsHtml += `<div class="col-md-4"><div class="alert alert-${sjStatus} mb-0"><strong>${data.sources.superjob.count}</strong><br>SuperJob</div></div>`;
            }

            statsHtml += '</div>';

            searchStatsDiv.innerHTML = statsHtml;

            // Список вакансий
            let vacanciesHtml = '';

            if (data.vacancies.length > 0) {
                data.vacancies.forEach(function(vacancy) {
                    const title = vacancy.title || 'Не указано';
                    const company = vacancy.company || 'Не указано';
                    const salary = vacancy.salary || 'Не указана';
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
                                        <h5 class="card-title">${title}</h5>
                                        <p class="card-text">
                                            <strong>Компания:</strong> ${company}<br>
                                            <strong>Зарплата:</strong> ${salary}
                                        </p>
                                    </div>
                                    <div>
                                        <span class="badge bg-${sourceClass}">${sourceName}</span>
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

            vacanciesListDiv.innerHTML = vacanciesHtml;
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }

        function showError(message) {
            errorAlert.textContent = message;
            errorAlert.style.display = 'block';
        }

        function hideError() {
            errorAlert.style.display = 'none';
        }

        // Проверяем API при загрузке
        fetch('/api/health')
            .then(response => response.json())
            .then(data => console.log('✅ API статус:', data))
            .catch(error => console.error('❌ API недоступен:', error));
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
            hh_vacancies = hh_parser.search(query, limit=15)
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
            sj_vacancies = sj_parser.search(query, limit=15)
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


if __name__ == '__main__':
    print("🚀 Запуск Job Parser System v2.0")
    print("=" * 50)
    print("🌐 Главная: http://localhost:5000")
    print("📊 API: http://localhost:5000/api/health")
    print("📋 Текст: http://localhost:5000/vacancies/text")
    print("📥 CSV: http://localhost:5000/export/csv")
    print("=" * 50)
    print("📡 Парсеры: HH.ru + SuperJob")
    print("💾 База данных: SQLite")
    print("✅ Готов к работе!")

    app.run(host='0.0.0.0', port=5000, debug=True)
