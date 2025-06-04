/**
 * Sistema Inteligente de Autocomplete para Medicamentos
 * Baseado no histórico de prescrições do médico
 */

// Configuração do autocomplete inteligente de medicamentos
function setupMedicamentAutoCompleteInteligente() {
    const medicamentInputs = document.querySelectorAll('input[id^="principio_ativo_"], input.medicamento-autocomplete');
    console.log('Inputs encontrados para autocomplete:', medicamentInputs.length);
    
    medicamentInputs.forEach((input, index) => {
        console.log(`Configurando input ${index}:`, input.id);
        
        // Remover listeners antigos para evitar conflitos
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        
        newInput.addEventListener('input', function() {
            const query = this.value;
            console.log('Input detectado:', query);
            
            if (query.length < 2) {
                hideMedicamentSuggestions(newInput);
                return;
            }
            
            console.log('Fazendo busca para:', query);
            // Usar API do histórico para autocomplete inteligente
            fetch('/api/medicamentos_historico?q=' + encodeURIComponent(query))
                .then(response => {
                    console.log('Resposta da API:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Dados recebidos:', data);
                    showMedicamentSuggestionsInteligente(newInput, data);
                })
                .catch(error => {
                    console.error('Erro na API:', error);
                });
        });
        
        // Auto-preenchimento ao selecionar medicamento
        newInput.addEventListener('blur', function() {
            setTimeout(() => {
                const principio = this.value.trim();
                if (principio && this.value.length > 2) {
                    autoPreencherMedicamentoHistorico(newInput, principio);
                }
            }, 200);
        });
    });
}

function showMedicamentSuggestionsInteligente(input, medicamentos) {
    // Remove suggestions existentes
    hideMedicamentSuggestions(input);
    
    if (medicamentos.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'autocomplete-suggestions-inteligente';
    suggestions.style.cssText = `
        position: absolute; 
        top: 100%; 
        left: 0; 
        right: 0; 
        background: rgba(30, 30, 30, 0.95); 
        border: 1px solid rgba(255, 255, 255, 0.2); 
        border-radius: 8px; 
        max-height: 200px; 
        overflow-y: auto; 
        z-index: 1000;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    `;
    
    medicamentos.forEach((med, index) => {
        const div = document.createElement('div');
        div.style.cssText = `
            padding: 12px; 
            cursor: pointer; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            transition: all 0.3s ease;
        `;
        
        const principio = med.principio_ativo || '';
        const info = [];
        if (med.concentracao) info.push(med.concentracao);
        if (med.via) info.push(med.via);
        if (med.frequencia) info.push(med.frequencia);
        
        div.innerHTML = `
            <div style="font-weight: bold; font-size: 14px;">${principio}</div>
            <small style="color: #aaa; font-size: 12px;">${info.join(' • ')} ${med.vezes_prescrito ? `(${med.vezes_prescrito}x prescrito)` : ''}</small>
        `;
        
        div.addEventListener('mouseenter', () => {
            div.style.backgroundColor = 'rgba(0, 123, 255, 0.2)';
            div.style.transform = 'translateX(5px)';
        });
        
        div.addEventListener('mouseleave', () => {
            div.style.backgroundColor = 'transparent';
            div.style.transform = 'translateX(0)';
        });
        
        div.addEventListener('click', () => {
            input.value = principio;
            suggestions.remove();
            // Auto-preencher campos baseado no histórico
            preencherCamposMedicamentoInteligente(input, med);
        });
        
        suggestions.appendChild(div);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

function hideMedicamentSuggestions(input) {
    const existingSuggestions = input.parentNode.querySelector('.autocomplete-suggestions-inteligente');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
}

function preencherCamposMedicamentoInteligente(principioInput, medicamento) {
    const row = principioInput.closest('.medicamento-row');
    if (!row) return;
    
    // Preencher campos baseado no histórico
    const concentracaoInput = row.querySelector('input[id^="concentracao_"]');
    const viaInput = row.querySelector('input[id^="via_"]');
    const frequenciaInput = row.querySelector('input[id^="frequencia_"]');
    const quantidadeInput = row.querySelector('input[id^="quantidade_"]');
    
    if (concentracaoInput && medicamento.concentracao) {
        concentracaoInput.value = medicamento.concentracao;
        animateFieldFill(concentracaoInput);
    }
    
    if (viaInput && medicamento.via) {
        viaInput.value = medicamento.via;
        animateFieldFill(viaInput);
    }
    
    if (frequenciaInput && medicamento.frequencia) {
        frequenciaInput.value = medicamento.frequencia;
        animateFieldFill(frequenciaInput);
    }
    
    if (quantidadeInput && medicamento.quantidade) {
        quantidadeInput.value = medicamento.quantidade;
        animateFieldFill(quantidadeInput);
    }
    
    // Exibir notificação de preenchimento automático
    showAutoFillNotificationInteligente(medicamento);
}

function autoPreencherMedicamentoHistorico(input, principio) {
    // Buscar dados do medicamento mais prescrito
    fetch('/api/medicamento_dados/' + encodeURIComponent(principio))
        .then(response => response.json())
        .then(data => {
            if (Object.keys(data).length > 0) {
                preencherCamposMedicamentoInteligente(input, data);
            }
        })
        .catch(error => console.error('Erro ao buscar dados do medicamento:', error));
}

function animateFieldFill(field) {
    field.style.transition = 'all 0.3s ease';
    field.style.backgroundColor = 'rgba(40, 167, 69, 0.2)';
    field.style.borderColor = '#28a745';
    
    setTimeout(() => {
        field.style.backgroundColor = '';
        field.style.borderColor = '';
    }, 1000);
}

function showAutoFillNotificationInteligente(medicamento) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.9), rgba(25, 135, 84, 0.9));
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        z-index: 10000;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: slideInRight 0.5s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.2);
    `;
    
    notification.innerHTML = `
        <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">
            <span style="color: #90EE90;">✓</span> Campos preenchidos automaticamente
        </div>
        <small style="opacity: 0.8;">Baseado no histórico de ${medicamento.vezes_prescrito || 1}x prescrições</small>
    `;
    
    // Adicionar estilos de animação
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    
    if (!document.querySelector('#autocomplete-animations')) {
        style.id = 'autocomplete-animations';
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-in';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 4000);
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que outros scripts carregaram
    setTimeout(() => {
        setupMedicamentAutoCompleteInteligente();
        console.log('Sistema de autocomplete inteligente inicializado');
    }, 500);
});

// Reinicializar quando novos medicamentos forem adicionados
function reinicializarAutocompleteInteligente() {
    setupMedicamentAutoCompleteInteligente();
}

// Exportar função para uso global
window.reinicializarAutocompleteInteligente = reinicializarAutocompleteInteligente;