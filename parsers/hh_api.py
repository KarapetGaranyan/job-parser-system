import requests

def fetch_hh_vacancies(query, page=0, per_page=20):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "page": page,
        "per_page": per_page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data['items'] 