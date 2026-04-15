function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        // Сохраняем исходный текст в data-атрибут
        button.dataset.originalText = button.innerHTML;
        // Вставляем спиннер Bootstrap
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span class="visually-hidden">Загрузка...</span>
        `;
    } else {
        // Восстанавливаем исходное содержимое
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
        button.disabled = false;
    }
}