function confirmAdmin() {
    if (confirm('Вы уверены? Панель админа является встроенным по умолчанию инструментом, и неумение ей пользоваться можешь навредить программе.')) {
        window.location.href = '/admin';
    }
    else { }
}


function logoutTooltip() {
    const button = document.getElementById('logout');
    const tooltip = button.dataset.tooltip;
    let tooltipElem;

    button.onmouseenter = function() {
        tooltipElem = document.createElement('div');
        tooltipElem.className = 'logout-tooltip';
        tooltipElem.innerHTML = tooltip;
        button.parentElement.append(tooltipElem);

        // 2. Позиционируем её над кнопкой
        let coords = this.getBoundingClientRect();

        let left = coords.left + (this.offsetWidth - tooltipElem.offsetWidth) / 2;
        let top = coords.top - tooltipElem.offsetHeight - 5;

        tooltipElem.style.left = left + 'px';
        tooltipElem.style.top = top + 'px';
    };

    button.onmouseleave = function() {
        if (tooltipElem) {
            tooltipElem.remove();
            tooltipElem = null;
        }
    };
}


document.addEventListener('DOMContentLoaded', function() {
    const adminBtn = document.querySelector('#admin');
    if (adminBtn) {
        adminBtn.addEventListener('click', confirmAdmin);
    }

    logoutTooltip();
});