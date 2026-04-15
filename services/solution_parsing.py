import re
from html import escape


def parse_numbered_list(text):
    """Парсит нумерованный список или одиночный текст"""
    text = text.strip()

    # Проверяем, есть ли нумерация (1), 2), ...)
    if re.search(r'^\d+\)', text):
        items = re.split(r'\n?\d+\)\s*', text)
        items = [item.strip() for item in items if item.strip()]
        return items, True  # True = есть нумерация
    else:
        return [text], False  # False = нет нумерации


def parse_recommendations(text):
    """Парсит аргументы с заголовками или без"""
    text = text.strip()
    result = []
    current_rec = None
    current_items = []

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Проверяем заголовок рекомендации
        match = re.match(r'Для рекомендации №(\d+):', line)
        if match:
            if current_rec is not None:
                result.append({'num': current_rec, 'items': current_items})
            current_rec = match.group(1)
            current_items = []
        # Проверяем элемент списка
        elif line.startswith('-'):
            current_items.append(line[1:].strip())

    # Добавляем последнюю группу
    if current_items:
        if current_rec is not None:
            result.append({'num': current_rec, 'items': current_items})
        else:
            result.append({'num': None, 'items': current_items})

    return result


def generate_html_numbered(items, has_numbering):
    """Генерирует HTML для нумерованного списка"""
    if has_numbering:
        html = '<ol class="list-group list-group-numbered mb-3">\n'
        for item in items:
            html += f'  <li class="list-group-item">{escape(item)}</li>\n'
        html += '</ol>'
    else:
        html = '<p class="mb-3">' + escape(items[0]) + '</p>'
    return html


def generate_html_recommendations(recs):
    """Генерирует HTML для рекомендаций"""
    html = ''

    if len(recs) == 1 and recs[0]['num'] is None:
        html += '<ul class="list-group mb-3">\n'
        for item in recs[0]['items']:
            html += f'  <li class="list-group-item">{escape(item)}</li>\n'
        html += '</ul>'
    else:
        for rec in recs:
            if rec['num']:
                html += f'<p class="fw-semibold mb-2">Для рекомендации №{escape(rec["num"])}:</p>\n'
            html += '<ul class="list-group mb-3">\n'
            for item in rec['items']:
                html += f'  <li class="list-group-item">{escape(item)}</li>\n'
            html += '</ul>\n'

    return html


def generate_full_html(solution):
    text1 = solution.recommendation
    text2 = solution.arguments

    items1, has_numbering = parse_numbered_list(text1)
    html1 = generate_html_numbered(items1, has_numbering)

    recs2 = parse_recommendations(text2)
    html2 = generate_html_recommendations(recs2)

    return f"""
        <p class="fw-semibold mb-2">Рекомендации:</p>
        {html1}

        <p class="fw-semibold mb-2">Аргументы:</p>
        {html2}
    """

if __name__ == '__main__':
    # ==================== ТЕСТ 1: С нумерацией и заголовками ====================
    # print("=" * 60)
    # print("ТЕСТ 1: С нумерацией и заголовками")
    # print("=" * 60)

    text1 = """1) Слить раствор и как можно скорее сделать новый.
    2) Проверить растения на признаки ожогов."""

    text2 = """Для рекомендации №1:
    - Критическое отклонение температуры раствора требует решения со стороны человека.
    - Автоматическое действие в таком случае может быть недостаточным.
    - Однако самым простым способом является замена раствора.
    Для рекомендации №2:
    - Слишком высокий уровень света может повредить листья, поэтому нужен визуальный контроль."""

    # print(generate_full_html(text1, text2))

    # ==================== ТЕСТ 2: Без нумерации и без заголовков ====================
    # print("\n" + "=" * 60)
    # print("ТЕСТ 2: Без нумерации и без заголовков")
    # print("=" * 60)

    text1 = """Слить раствор и как можно скорее сделать новый."""

    text2 = """- Критическое отклонение температуры раствора требует решения со стороны человека.
    - Автоматическое действие в таком случае может быть недостаточным.
    - Однако самым простым способом является замена раствора."""

    # print(generate_full_html(text1, text2))