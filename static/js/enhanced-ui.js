// Enhanced UI Components for Sistema VIDAH
class VidahUI {
    static showLoading(element, text = 'Carregando...') {
        const originalContent = element.innerHTML;
        element.innerHTML = `
            <div class="d-flex align-items-center justify-content-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>${text}</span>
            </div>
        `;
        element.disabled = true;
        element.dataset.originalContent = originalContent;
    }

    static hideLoading(element) {
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
    }

    static showNotification(message, type = 'info', duration = 5000) {
        const notificationContainer = document.getElementById('notification-container') || 
            this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-item`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${this.getIconForType(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        notificationContainer.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    static createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    static getIconForType(type) {
        const icons = {
            'success': 'fa-check-circle',
            'danger': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation-circle',
            'info': 'fa-info-circle'
        };
        return icons[type] || icons['info'];
    }

    static confirmAction(message, title = 'Confirmar') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary confirm-btn">Confirmar</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            
            modal.querySelector('.confirm-btn').addEventListener('click', () => {
                resolve(true);
                bsModal.hide();
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                resolve(false);
                modal.remove();
            });
            
            bsModal.show();
        });
    }

    static enhanceForm(formElement) {
        // Add real-time validation
        const inputs = formElement.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });

        // Enhanced form submission
        formElement.addEventListener('submit', (e) => {
            const submitBtn = formElement.querySelector('button[type="submit"]');
            if (submitBtn) {
                this.showLoading(submitBtn, 'Processando...');
            }
        });
    }

    static validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'Este campo é obrigatório';
        }

        // CPF validation
        if (field.name === 'cpf' && value) {
            if (!this.validateCPF(value)) {
                isValid = false;
                message = 'CPF inválido';
            }
        }

        // Update field appearance
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            
            // Show error message
            let feedback = field.parentNode.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.appendChild(feedback);
            }
            feedback.textContent = message;
        }

        return isValid;
    }

    static validateCPF(cpf) {
        cpf = cpf.replace(/[^\d]/g, '');
        
        // Accept any numeric sequence between 8-11 digits
        return cpf.length >= 8 && cpf.length <= 11;
    }

    static formatCPF(input) {
        let value = input.value.replace(/\D/g, '');
        
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        }
        
        input.value = value;
    }

    static addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S to save (prevent default and trigger submit)
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const form = document.querySelector('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true }));
                }
            }
            
            // Ctrl+N for new record
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                const newBtn = document.querySelector('[data-action="new"]');
                if (newBtn) newBtn.click();
            }
            
            // Escape to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                });
            }
        });
    }
}

// Initialize enhanced UI when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Enhance all forms
    document.querySelectorAll('form').forEach(form => {
        VidahUI.enhanceForm(form);
    });
    
    // Add keyboard shortcuts
    VidahUI.addKeyboardShortcuts();
    
    // Auto-format CPF fields
    document.querySelectorAll('input[name="cpf"]').forEach(input => {
        input.addEventListener('input', () => VidahUI.formatCPF(input));
    });
    
    // Global error handler for fetch requests
    window.addEventListener('unhandledrejection', (e) => {
        VidahUI.showNotification('Erro de conexão. Tente novamente.', 'danger');
    });
});
// Configuração do autocomplete de pacientes
function setupPatientAutocomplete() {
    const nomeInput = document.getElementById('nome_paciente');
    if (!nomeInput) return;
    
    nomeInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 2) return;
        
        fetch('/api/pacientes?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                showPatientSuggestions(data, nomeInput);
            })
            .catch(error => console.error('Erro ao buscar pacientes:', error));
    });
}

function showPatientSuggestions(patients, input) {
    // Remover sugestões anteriores
    const existingSuggestions = document.querySelector('.patient-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (patients.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'patient-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        width: 100%;
    `;
    
    patients.forEach(patient => {
        const div = document.createElement('div');
        div.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
        div.textContent = patient.nome;
        div.addEventListener('click', () => {
            selectPatient(patient);
            suggestions.remove();
        });
        suggestions.appendChild(div);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

function selectPatient(patient) {
    // Preencher dados do paciente
    const nomeInput = document.getElementById('nome_paciente');
    const cpfInput = document.getElementById('cpf');
    const idadeInput = document.getElementById('idade');
    const enderecoInput = document.getElementById('endereco');
    const cidadeInput = document.getElementById('cidade');
    
    if (nomeInput) nomeInput.value = patient.nome;
    if (cpfInput) cpfInput.value = patient.cpf || '';
    if (idadeInput) idadeInput.value = patient.idade || '';
    if (enderecoInput) enderecoInput.value = patient.endereco || '';
    if (cidadeInput) cidadeInput.value = patient.cidade || '';
}

// Configuração do autocomplete de medicamentos
function setupMedicamentAutocomplete() {
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('medicamento-input')) {
            const query = e.target.value;
            if (query.length < 2) return;
            
            fetch('/api/medicamentos?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    showMedicamentSuggestions(data, e.target);
                })
                .catch(error => console.error('Erro ao buscar medicamentos:', error));
        }
    });
}

function showMedicamentSuggestions(medicaments, input) {
    // Remover sugestões anteriores
    const existingSuggestions = document.querySelector('.medicament-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (medicaments.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'medicament-suggestions';
    suggestions.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        width: 100%;
    `;
    
    medicaments.forEach(med => {
        const div = document.createElement('div');
        div.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
        div.textContent = med.nome;
        div.addEventListener('click', () => {
            input.value = med.nome;
            suggestions.remove();
        });
        suggestions.appendChild(div);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    setupPatientAutocomplete();
    setupMedicamentAutocomplete();
});
