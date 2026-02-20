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
                    new_done.appendChild(row.querySelector('label'));
                    new_done.appendChild(row.querySelector('a'));
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