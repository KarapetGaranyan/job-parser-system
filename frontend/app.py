from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hh_search', methods=['POST'])
def hh_search():
    data = request.json
    resp = requests.post('http://localhost:5000/api/search_all', json=data)
    try:
        return jsonify(resp.json())
    except Exception:
        return jsonify({'error': 'Ошибка при получении данных с backend'}), 500

@app.route('/api/search_all', methods=['POST'])
def search_all():
    try:
        # ...весь ваш код...
        return jsonify({'vacancies': hh_vacancies + sj_vacancies})
    except Exception as e:
        import traceback
        print('Ошибка в search_all:', traceback.format_exc())
        return jsonify({'error': f'Ошибка на сервере: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)