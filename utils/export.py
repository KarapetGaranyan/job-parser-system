import csv

def export_vacancies_to_csv(vacancies, filename):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Название', 'Компания', 'Местоположение', 'Зарплата', 'Описание', 'Дата публикации'])
        for v in vacancies:
            writer.writerow([
                v.id, v.title, v.company, v.location, v.salary, v.description, v.published_at
            ]) 