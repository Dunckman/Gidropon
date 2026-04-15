const csrftoken = document.querySelector('meta[name="csrf-token"]').content;


function deletePlant() {
    const button = document.querySelector('.delete');

    button.disabled = true;

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
        if (data.success && data.redirect_url) {
            window.location.href = data.redirect_url;
            return;
        }

        button.disabled = false;
        button.textContent = 'Ошибка';
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');

        setTimeout(() => {
            button.classList.remove('btn-danger');
            button.classList.add('btn-success');
            button.textContent = 'Удалено';
        }, 5000);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        button.disabled = false;
        alert('Ошибка подключения к серверу.');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const deleteBtn = document.querySelector('.delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', deletePlant);
    }
});
