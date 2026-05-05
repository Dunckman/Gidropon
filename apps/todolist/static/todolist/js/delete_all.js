const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrftoken = csrfMeta ? csrfMeta.content : '';

function deletePlantLocation(event) {
    const button = event.currentTarget;
    const deleteObject = (button.dataset.object || '').toLowerCase();

    let confirmMessage = '';
    if (deleteObject === 'plant') {
        confirmMessage = 'Вы уверены, что хотите удалить растение? Вместе с ним удалятся его стадии роста и действия.';
    } else if (deleteObject === 'location') {
        confirmMessage = 'Вы уверены, что хотите удалить расположение?';
    } else if (deleteObject === 'user') {
        confirmMessage = 'Вы уверены, что хотите удалить пользователя?';
    } else {
        confirmMessage = 'Вы уверены, что хотите удалить объект?';
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    button.disabled = true;

    fetch(button.dataset.url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success && data.redirect_url) {
                window.location.href = data.redirect_url;
                return;
            }

            button.disabled = false;
            button.textContent = data.error || 'Ошибка';
            button.classList.remove('btn-success');
            button.classList.add('btn-danger');
        })
        .catch((error) => {
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
}

function deleteAction() {
    alert('Действие удаляется только вместе с растением.');

    if (confirm('Желаете перейти к удалению растения?')) {
        const button = document.getElementById('delete-action');
        const plantId = button.dataset.plant_id;
        window.location.href = `/todolist/plant/${plantId}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
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
