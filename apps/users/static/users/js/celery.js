function pollTaskStatus(task_id, originalText, class_name, options = {}) {
    const button = document.querySelector(`.${class_name}`);
    const maxAttempts = Number.isInteger(options.maxAttempts) ? options.maxAttempts : 40;
    let attempts = 0;

    const interval = setInterval(() => {
        attempts += 1;
        if (attempts > maxAttempts) {
            clearInterval(interval);
            if (typeof options.onTimeout === 'function') {
                options.onTimeout();
            }
            return;
        }

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

    return interval;
}

function showButtonError(button, originalText) {
    const initialClassName = button.dataset.initialClassName || button.className;
    if (!button.dataset.initialClassName) {
        button.dataset.initialClassName = initialClassName;
    }

    button.disabled = true;
    button.textContent = 'Ошибка';

    button.classList.remove('btn-primary', 'btn-success', 'btn-outline-success');
    button.classList.add('btn-outline-danger');

    setTimeout(() => {
        button.disabled = false;
        button.textContent = originalText;
        button.className = button.dataset.initialClassName || initialClassName;
    }, 5000);
}
