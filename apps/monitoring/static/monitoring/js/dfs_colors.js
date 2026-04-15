const colors = JSON.parse(document.getElementById('colors').textContent);

document.addEventListener("DOMContentLoaded", function() {
    for (let key in colors) {
        let parameter = document.querySelector(`#${key}`);
        const value = parameter.textContent;

        if (colors[key] === 'normal') {
            parameter.textContent = value;
            parameter.style.color = 'green';
        }
        else if (colors[key] === 'critical_minimum') {
            parameter.textContent = `${value}\u2B07`;
            parameter.style.color = 'red';
        }
        else if (colors[key] === 'critical_maximum') {
            parameter.textContent = `${value}\u2B06`;
            parameter.style.color = 'red';
        }
        else if (colors[key] === 'minimum') {
            parameter.textContent = `${value}\u2B07`;
            parameter.style.color = 'orange';
        }
        else if (colors[key] === 'maximum') {
            parameter.textContent = `${value}\u2B06`;
            parameter.style.color = 'orange';
        }
        else {
            parameter.textContent = 'ERROR';
        }
    }
});