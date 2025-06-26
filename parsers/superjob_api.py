import requests

def fetch_superjob_vacancies(query, vacancies_count=20):
    url = 'https://api.superjob.ru/2.0/vacancies'
    secret = 'v3.r.137222938.adcc1bf5602cc5a2c697d63eb9c580dd5029f96f.049aae965267ebe71bbc7c587187da62cdbc560e'
    per_page = 20
    page = 0
    result = []
    headers = {
        'X-Api-App-Id': secret,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while per_page * page < vacancies_count:
        params = {
            'keyword': query,
            'page': page,
            'count': per_page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for obj in data.get('objects', []):
                salary = ''
                if obj.get('payment_from', 0) and obj.get('payment_to', 0):
                    salary = f"{obj['payment_from']} - {obj['payment_to']} {obj.get('currency', '')}"
                elif obj.get('payment_from', 0):
                    salary = f"от {obj['payment_from']} {obj.get('currency', '')}"
                elif obj.get('payment_to', 0):
                    salary = f"до {obj['payment_to']} {obj.get('currency', '')}"
                else:
                    salary = 'Зарплата не указана'
                vac = {
                    'title': obj.get('profession', ''),
                    'company': obj.get('firm_name', ''),
                    'location': obj.get('town', {}).get('title', ''),
                    'salary': salary,
                    'description': obj.get('candidat', ''),
                    'published_at': obj.get('date_published', None),
                    'link': obj.get('link', '')
                }
                result.append(vac)
            if not data.get('more', False):
                break
            page += 1
        else:
            break
    return result 