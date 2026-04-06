// Получаем CSRF из meta-тега
const csrftoken = document.querySelector('meta[name="csrf-token"]').content;

function markDone() {
    const button = document.querySelector('.mark-done');
    const id = button.dataset.id;
    let comment = prompt('Введите комментарий об устранении аварии:', 'Авария устранена в соответствии с рекомендацией')
    const url = button.dataset.url.replace('/0/', `/${id}/`).replace('/solved/', `/${comment}/`);

    button.disabled = true;
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data =>{
        if (data.success) {
            location.reload();
        } else {
            // Ошибка — снимаем галочку
            alert('Не удалось отметить аварию устранённой.');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу.');
    });
}

function checkNew() {
    const button = document.querySelector('.check-new');
    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = 'Проверка...';   // или добавь спиннер

    fetch(button.dataset.url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success || !data.task_id) {
            throw new Error(data.error || 'Не удалось запустить проверку');
        }

        // Начинаем опрашивать статус
        pollTaskStatus(data.task_id, originalText);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert(error.message || 'Ошибка при запуске проверки');
        resetButton(button, originalText);
    });
}

function pollTaskStatus(task_id, originalText) {
    const button = document.querySelector('.check-new');

    const interval = setInterval(() => {
        fetch(`/monitoring/task-status/${task_id}/`)   // поменяй путь если нужно
            .then(response => response.json())
            .then(data => {
                if (data.status === 'SUCCESS') {
                    clearInterval(interval);
                    location.reload();                    // ← Автоперезагрузка страницы
                }
                else if (data.status === 'FAILURE') {
                    clearInterval(interval);
                    alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                    resetButton(button, originalText);
                }
                else if (data.status === 'STARTED' || data.status === 'PENDING') {
                    // можно обновить текст кнопки, например "Выполняется..."
                    button.textContent = 'Выполняется...';
                }
                // можно добавить 'PROGRESS' и показывать прогресс, если реализуешь
            })
            .catch(err => {
                console.error(err);
                // не прерываем polling при мелкой ошибке сети
            });
    }, 1500);   // проверяем каждые 1.5 секунды
}

function resetButton(button, originalText) {
    button.disabled = false;
    button.textContent = originalText;
}

document.addEventListener('DOMContentLoaded', function() {
    const checkBtn = document.querySelector('.check-new');
    if (checkBtn) {
        checkBtn.addEventListener('click', checkNew);
    }

    const markBtn = document.querySelector('.mark-done');
    if (markBtn) {
        markBtn.addEventListener('click', markDone);
    }
});