// Получаем CSRF из meta-тега
const csrftoken = document.querySelector('meta[name="csrf-token"]').content;
// Получаем базовый URL из data-атрибута контейнера
const baseUrl = document.getElementById('awaits-tasks-container').dataset.markDoneUrl;


document.querySelectorAll('.task-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const taskId = this.dataset.taskId;
        const row = document.getElementById(`task-row-${taskId}`);
        const dones = document.getElementById('dones-list');

        if (this.checked) {
            const url = baseUrl.replace('/0/', `/${taskId}/`);

            // Отправляем AJAX-запрос
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Сразу удаляем строку
                    row.remove();
                    const container = document.getElementById('awaits-tasks-container');
                    if (container.querySelectorAll('.task-row').length === 0) {
                        container.innerHTML = '<p>На выбранную дату задач нет.</p>';
                    }

                    let new_done = document.createElement('li');
                    new_done.className = 'list-group-item d-flex align-items-center';

                    const text = document.createElement('span');
                    text.className = 'flex-grow-1';
                    text.textContent = row.querySelector('label').textContent;

                    const link = document.createElement('a');
                    link.className = 'btn btn-sm btn-outline-primary';
                    link.href = row.querySelector('a').href;
                    link.textContent = 'Подробнее';

                    new_done.appendChild(text);
                    new_done.appendChild(link);
                    dones.appendChild(new_done);
                } else {
                    // Ошибка — снимаем галочку
                    this.checked = false;
                    alert('Не удалось обновить статус задачи.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                this.checked = false;
                alert('Ошибка подключения к серверу.');
            });
        }
    });
});


function addTasks() {
    const button = document.querySelector('.add-tasks');
    const originalText = button.textContent; // Запоминаем текст ("Обновить")

    // Включаем спиннер
    setButtonLoading(button, true, originalText);

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
        // Запускаем опрос статуса (функция в celery.js)
        pollTaskStatus(data.task_id, originalText, 'add-tasks');
    })
    .catch(error => {
        console.error('Ошибка запуска:', error);
        alert(error.message);
        // При ошибке запуска сразу показываем красную кнопку
        showButtonError(button, originalText);
    });
}


document.addEventListener('DOMContentLoaded', function() {
    const checkBtn = document.querySelector('.add-tasks');
    if (checkBtn) {
        checkBtn.addEventListener('click', addTasks);
    }
});