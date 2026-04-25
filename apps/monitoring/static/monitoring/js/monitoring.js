const csrftoken = document.querySelector('meta[name="csrf-token"]').content;
const CHECK_NEW_TASK_STORAGE_KEY = 'monitoring_check_new_task_id';

function markDone() {
    const button = document.querySelector('.mark-done');
    const id = button.dataset.id;
    const comment = prompt(
        'Введите комментарий об устранении аварии:',
        'Авария устранена в соответствии с рекомендацией.'
    );
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
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                button.disabled = false;
                button.textContent = 'Ошибка';
                button.classList.remove('btn-success');
                button.classList.add('btn-danger');

                setTimeout(() => {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-success');
                    button.textContent = 'Выполнено';
                }, 5000);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            button.disabled = false;
            alert('Ошибка подключения к серверу.');
        });
}

function startCheckNewPolling(taskId) {
    const button = document.querySelector('.check-new');
    if (!button) {
        return;
    }

    const originalText = button.dataset.originalText || button.textContent;
    setButtonLoading(button, true);

    pollTaskStatus(taskId, originalText, 'check-new', {
        onSuccess: () => {
            localStorage.removeItem(CHECK_NEW_TASK_STORAGE_KEY);
        },
        onFailure: () => {
            localStorage.removeItem(CHECK_NEW_TASK_STORAGE_KEY);
        }
    });
}

function checkNew() {
    const button = document.querySelector('.check-new');

    setButtonLoading(button, true);

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
                alert(data.error || 'Не удалось запустить проверку');
                throw new Error(data.error || 'Не удалось запустить проверку');
            }

            localStorage.setItem(CHECK_NEW_TASK_STORAGE_KEY, data.task_id);
            startCheckNewPolling(data.task_id);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            localStorage.removeItem(CHECK_NEW_TASK_STORAGE_KEY);
            showButtonError(button, button.dataset.originalText || 'Проверить');
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const checkBtn = document.querySelector('.check-new');
    if (checkBtn) {
        checkBtn.addEventListener('click', checkNew);

        const savedTaskId = localStorage.getItem(CHECK_NEW_TASK_STORAGE_KEY);
        if (savedTaskId) {
            startCheckNewPolling(savedTaskId);
        }
    }

    const markBtn = document.querySelector('.mark-done');
    if (markBtn) {
        markBtn.addEventListener('click', markDone);
    }
});
