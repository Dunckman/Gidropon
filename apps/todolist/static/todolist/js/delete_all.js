const csrftoken = document.querySelector('meta[name="csrf-token"]').content;


function deletePlantLocation() {
    const button = document.querySelector('.delete-object');
    const deleteObject = button.dataset.object;

    let confirmMessage = '';
    if (deleteObject === 'растение') {
        confirmMessage = 'Вы уверены, что хотите удалить растение? Вместе с ним удалятся его стадии роста и действия.';
    }
    else if (deleteObject === 'расположение') {
        confirmMessage = 'Вы уверены, что хотите удалить расположение?'
    }
    else {
        confirmMessage = 'Ошибка.'
    }
    if (!confirm(confirmMessage)) {
        return;
    }

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


function deleteStage() {
    alert('Стадия роста удаляется только вместе с растением.');

    if (confirm('Желаете перейти к удалению растения?')) {
        const button = document.getElementById('delete-stage');
        const plantId = button.dataset.plant;

        window.location.href = `/todolist/plant/${plantId}`;
    }
    else { }
}


function deleteAction() {
    alert('Действие удаляется только вместе с растением.');

    if (confirm('Желаете перейти к удалению растения?')) {
        const button = document.getElementById('delete-action');
        const plantId = button.dataset.plant_id;

        window.location.href = `/todolist/plant/${plantId}`;
    }
    else { }
}


document.addEventListener('DOMContentLoaded', function() {
    const plantLocationBtn = document.querySelector('.delete-object');
    if (plantLocationBtn) {
        plantLocationBtn.addEventListener('click', deletePlantLocation);
    }

    const stageBtn = document.querySelector('#delete-stage');
    if (stageBtn) {
        stageBtn.addEventListener('click', deleteStage);
    }

    const actionBtn = document.querySelector('#delete-action');
    if (actionBtn) {
        actionBtn.addEventListener('click', deleteAction);
    }
});
