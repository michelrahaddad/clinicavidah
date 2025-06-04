
// Sistema Médico VIDAH - JavaScript Functions
function confirmarExclusao(mensagem) {
    return confirm(mensagem || 'Tem certeza que deseja excluir este item?');
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

function buscarPaciente() {
    const termo = document.getElementById('busca_paciente').value;
    if (termo.length >= 3) {
        fetch(`/api/buscar_pacientes?q=${termo}`)
            .then(response => response.json())
            .then(data => {
                // Implementar autocomplete
                console.log(data);
            });
    }
}

function validarFormulario(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    for (let input of inputs) {
        if (!input.value.trim()) {
            alert('Por favor, preencha todos os campos obrigatórios.');
            input.focus();
            return false;
        }
    }
    return true;
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Configurações gerais
    console.log('Sistema Médico VIDAH carregado');
});
