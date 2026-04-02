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
            alert('Не удалось обновить статус задачи.');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка подключения к серверу.');
    });
}

const data = JSON.parse(document.getElementById('colors').textContent);
document.addEventListener("DOMContentLoaded", function() {
    for (let key in data) {
        let parameter = document.querySelector(`#${key}`);
        const value = parameter.textContent;

        if (data[key] === 'normal') {
            parameter.textContent = value;
            parameter.style.color = 'green';
        }
        else if (data[key] === 'critical_minimum') {
            parameter.textContent = `${value}\u2B07`;
            parameter.style.color = 'red';
        }
        else if (data[key] === 'critical_maximum') {
            parameter.textContent = `${value}\u2B06`;
            parameter.style.color = 'red';
        }
        else if (data[key] === 'minimum') {
            parameter.textContent = `${value}\u2B07`;
            parameter.style.color = 'orange';
        }
        else if (data[key] === 'maximum') {
            parameter.textContent = `${value}\u2B06`;
            parameter.style.color = 'orange';
        }
        else {
            parameter.textContent = 'ERROR';
        }
    }
});