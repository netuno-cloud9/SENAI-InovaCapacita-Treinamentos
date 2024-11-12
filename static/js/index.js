// Add event listeners to all .bt elements
document.querySelectorAll('.bt').forEach(button => {
    button.addEventListener('click', () => {
        // Determine the URL to navigate to based on the button clicked
        let url = '';
        switch (button.id) {
            case 'indicadores':
                url = '../indicators/indicators.html';
                break;
            case 'planos-de-aula':
                url = '../classplan/classplan.html';
                break;
            case 'links-rapidos':
                url = '../splinks';
                break;
            case 'educhat':
                url = '/content/educhat.html';
                break;
            case 'ranking':
                url = '/content/ranking.html';
                break;
            case 'suporte-tecnico':
                url = '/content/suporte_tecnico.html';
                break;
        }
        // Apply a click animation
        button.classList.add('clicked');

        // Redirect to the selected URL after a short delay
        setTimeout(() => {
            window.location.href = url;
        }, 300); // Adjust delay time as needed
    });
});
