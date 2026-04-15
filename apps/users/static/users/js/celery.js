function pollTaskStatus(task_id, originalText, class_name, options = {}) {
    const button = document.querySelector(`.${class_name}`);

    const interval = setInterval(() => {
        fetch(`/task-status/${task_id}/`)
            .then(response => response.json())
            .then(data => {
                const status = String(data.status).toUpperCase();

                if (status === 'SUCCESS') {
                    clearInterval(interval);
                    if (typeof options.onSuccess === 'function') {
                        options.onSuccess(data);
                    }
                    location.reload();
                }
                else if (status === 'FAILURE') {
                    clearInterval(interval);
                    if (typeof options.onFailure === 'function') {
                        options.onFailure(data);
                    }
                    showButtonError(button, originalText);
                }
                else if (status === 'STARTED' || status === 'PENDING') {
                    if (typeof options.onPending === 'function') {
                        options.onPending(data);
                    }
                }
            })
            .catch(err => {
                if (typeof options.onError === 'function') {
                    options.onError(err);
                }
                console.error('Network error while polling task status:', err);
            });
    }, 1500);
}

function showButtonError(button, originalText) {
    button.disabled = true;
    button.textContent = 'Ошибка';

    button.classList.remove('btn-outline-success');
    button.classList.add('btn-outline-danger');

    setTimeout(() => {
        button.disabled = false;
        button.textContent = originalText;
        button.classList.remove('btn-outline-danger');
        button.classList.add('btn-outline-success');
    }, 5000);
}
