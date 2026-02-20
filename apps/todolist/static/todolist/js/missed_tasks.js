// Получаем CSRF из meta-тега
const csrftoken = document.querySelector('meta[name="csrf-token"]').content;
// Получаем базовый URL из data-атрибута контейнера
const baseUrl = document.getElementById('tasks-container').dataset.markDoneUrl;

document.querySelectorAll('.task-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const taskId = this.dataset.taskId;
        const row = document.getElementById(`task-row-${taskId}`);

        if (this.checked) {
            // Формируем правильный URL
            const url = baseUrl.replace('/0/', `/${taskId}/`);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    row.remove();
                    const container = document.getElementById('tasks-container');
                    if (container.querySelectorAll('.task-row').length === 0) {
                        container.innerHTML = '<p>На сегодня задач нет.</p>';
                    }
                } else {
                    this.checked = false;
                    alert('Не удалось обновить статус задачи: ' + (data.error || 'Неизвестная ошибка'));
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