document.querySelector('form').addEventListener('submit', function(e) {
    const cantidad = document.getElementById('cantidad').value;
    if (cantidad <= 0) {
        alert('La cantidad debe ser mayor a cero.');
        e.preventDefault();
    }
});
