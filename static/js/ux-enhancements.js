// UX Enhancements for Sistema Médico VIDAH

// Initialize UX enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeUXEnhancements();
});

function initializeUXEnhancements() {
    // Initialize all enhancement modules
    initLoadingStates();
    initScrollAnimations();
    initFormEnhancements();
    initToastNotifications();
    initQuickSearch();
    initProgressIndicators();
    initAccessibilityFeatures();
    initPageTransitions();
    
    console.log('UX Enhancements initialized');
}

// Loading States and Feedback
function initLoadingStates() {
    // Show loading overlay for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingOverlay();
        });
    });
    
    // Hide loading after page load
    window.addEventListener('load', function() {
        hideLoadingOverlay();
    });
}

function showLoadingOverlay(message = 'Carregando...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner"></div>
            <p class="text-light mt-3">${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
    }
}

// Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Add animation classes to cards and elements
    const animatedElements = document.querySelectorAll('.glass-card, .quick-action-card, .stats-card');
    animatedElements.forEach((el, index) => {
        const animationClass = index % 3 === 0 ? 'fade-in-up' : 
                              index % 3 === 1 ? 'fade-in-left' : 'fade-in-right';
        el.classList.add(animationClass);
        observer.observe(el);
    });
}

// Form Enhancements
function initFormEnhancements() {
    // Real-time validation
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidationError);
    });
    
    // Enhanced file inputs
    initFileInputs();
    
    // Auto-save functionality
    initAutoSave();
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Skip validation for optional fields
    if (!field.required && !value) return;
    
    let isValid = true;
    let errorMessage = '';
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Digite um email válido';
        }
    }
    
    // CPF validation
    if (field.name === 'cpf' && value) {
        if (!validateCPF(value)) {
            isValid = false;
            errorMessage = 'CPF inválido';
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato: (00) 00000-0000';
        }
    }
    
    // Required field validation
    if (field.required && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório';
    }
    
    // Apply validation feedback
    if (isValid) {
        field.classList.add('is-valid');
        removeErrorMessage(field);
    } else {
        field.classList.add('is-invalid');
        showErrorMessage(field, errorMessage);
    }
}

function clearValidationError(event) {
    const field = event.target;
    field.classList.remove('is-invalid');
    removeErrorMessage(field);
}

function showErrorMessage(field, message) {
    removeErrorMessage(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
    
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    return remainder === parseInt(cpf.charAt(10));
}

function initFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Nenhum arquivo selecionado';
            const label = this.nextElementSibling;
            if (label && label.tagName === 'LABEL') {
                label.textContent = fileName;
            }
        });
    });
}

function initAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                saveFormData(form);
            }, 2000));
        });
        
        // Load saved data on page load
        loadFormData(form);
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
    showToast('Rascunho salvo automaticamente', 'info', 2000);
}

function loadFormData(form) {
    const savedData = localStorage.getItem(`autosave_${form.id}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type !== 'password') {
                input.value = data[key];
            }
        });
    }
}

// Toast Notifications
function initToastNotifications() {
    // Create toast container if it doesn't exist
    if (!document.querySelector('.toast-container')) {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-body d-flex justify-content-between align-items-center">
            <span class="text-light">${message}</span>
            <button type="button" class="btn-close btn-close-white" onclick="this.closest('.toast').remove()"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Show toast with animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Quick Search Enhancement
function initQuickSearch() {
    const searchInputs = document.querySelectorAll('input[data-search]');
    searchInputs.forEach(input => {
        const suggestionContainer = createSuggestionContainer(input);
        
        input.addEventListener('input', debounce(() => {
            const query = input.value.trim();
            if (query.length >= 2) {
                performSearch(query, input.dataset.search, suggestionContainer);
            } else {
                hideSuggestions(suggestionContainer);
            }
        }, 300));
        
        input.addEventListener('blur', () => {
            setTimeout(() => hideSuggestions(suggestionContainer), 200);
        });
    });
}

function createSuggestionContainer(input) {
    const container = document.createElement('div');
    container.className = 'search-suggestions';
    input.parentNode.appendChild(container);
    return container;
}

function performSearch(query, endpoint, container) {
    fetch(`/api/${endpoint}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showSuggestions(data, container);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function showSuggestions(suggestions, container) {
    container.innerHTML = '';
    
    if (suggestions.length === 0) {
        container.innerHTML = '<div class="search-suggestion">Nenhum resultado encontrado</div>';
    } else {
        suggestions.forEach(item => {
            const suggestion = document.createElement('div');
            suggestion.className = 'search-suggestion';
            suggestion.textContent = item.nome || item.codigo || item;
            suggestion.addEventListener('click', () => selectSuggestion(item, container));
            container.appendChild(suggestion);
        });
    }
    
    container.style.display = 'block';
}

function hideSuggestions(container) {
    container.style.display = 'none';
}

function selectSuggestion(item, container) {
    const input = container.previousElementSibling;
    input.value = item.nome || item.codigo || item;
    hideSuggestions(container);
    input.dispatchEvent(new Event('change'));
}

// Progress Indicators
function initProgressIndicators() {
    const progressContainers = document.querySelectorAll('[data-progress]');
    progressContainers.forEach(container => {
        updateProgressIndicator(container);
    });
}

function updateProgressIndicator(container) {
    const steps = container.querySelectorAll('.progress-step');
    const currentStep = parseInt(container.dataset.currentStep) || 0;
    
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        if (index < currentStep) {
            step.classList.add('completed');
        } else if (index === currentStep) {
            step.classList.add('active');
        }
    });
}

// Accessibility Features
function initAccessibilityFeatures() {
    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardNavigation);
    
    // Focus management
    const focusableElements = document.querySelectorAll('button, input, select, textarea, a[href]');
    focusableElements.forEach(el => {
        el.addEventListener('focus', () => el.classList.add('focus-visible'));
        el.addEventListener('blur', () => el.classList.remove('focus-visible'));
    });
    
    // Skip links
    addSkipLinks();
}

function handleKeyboardNavigation(event) {
    // Escape key closes modals and dropdowns
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const closeBtn = openModal.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }
    }
    
    // Enter key on cards acts as click
    if (event.key === 'Enter' && event.target.classList.contains('quick-action-card')) {
        event.target.click();
    }
}

function addSkipLinks() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Pular para conteúdo principal';
    skipLink.className = 'sr-only sr-only-focusable';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: #000;
        color: #fff;
        padding: 8px;
        text-decoration: none;
        z-index: 10000;
    `;
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '6px';
    });
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
}

// Page Transitions
function initPageTransitions() {
    document.body.classList.add('page-transition');
    
    window.addEventListener('load', () => {
        document.body.classList.add('loaded');
    });
    
    // Handle navigation links
    const navLinks = document.querySelectorAll('a[href^="/"]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                navigateWithTransition(link.href);
            }
        });
    });
}

function navigateWithTransition(url) {
    document.body.classList.remove('loaded');
    showLoadingOverlay('Carregando página...');
    
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global utility functions for forms
window.UXEnhancements = {
    showToast,
    showLoadingOverlay,
    hideLoadingOverlay,
    validateField,
    updateProgressIndicator
};

// Auto-format inputs
document.addEventListener('input', function(e) {
    const input = e.target;
    
    // CPF formatting
    if (input.name === 'cpf') {
        let value = input.value.replace(/\D/g, '');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        input.value = value;
    }
    
    // Phone formatting
    if (input.type === 'tel') {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{2})(\d)/, '($1) $2');
            value = value.replace(/(\d{4,5})(\d{4})$/, '$1-$2');
            input.value = value;
        }
    }
});

console.log('UX Enhancements loaded successfully');