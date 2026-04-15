const csrftoken = document.querySelector('meta[name="csrf-token"]').content;

function markDone() {
    console.log('f');

    const button = document.querySelector('.mark-done');
    const url = button.dataset.url;

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
            // Ошибка — показываем на кнопке
            button.disabled = false;
            button.textContent = 'Ошибка';
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-outline-danger');

            setTimeout(() => {
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-outline-success');
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


document.addEventListener('DOMContentLoaded', function() {
    const markDoneBtn = document.querySelector('.mark-done');
    if (markDoneBtn) {
        markDoneBtn.addEventListener('click', markDone);
    }
});