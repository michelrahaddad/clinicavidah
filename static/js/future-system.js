/**
 * VIDAH Medical System - Future Neural JavaScript
 * Advanced interactions and animations for the medical system
 */

class NeuralSystem {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupFormValidation();
        this.setupCounters();
        this.setupNeuralEffects();
        this.setupLoadingStates();
        this.setupTooltips();
    }

    setupEventListeners() {
        // Auto-hide alerts
        this.setupAutoHideAlerts();
        
        // Neural button effects
        this.setupNeuralButtons();
        
        // Form enhancements
        this.setupFormEnhancements();
        
        // Navigation enhancements
        this.setupNavigationEnhancements();
    }

    setupAutoHideAlerts() {
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                try {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                } catch (e) {
                    // Bootstrap alert not initialized
                    alert.style.transition = 'all 0.5s ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-20px)';
                    setTimeout(() => alert.remove(), 500);
                }
            });
        }, 5000);
    }

    setupNeuralButtons() {
        document.querySelectorAll('.neural-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.createRippleEffect(e, btn);
            });

            btn.addEventListener('mouseenter', () => {
                this.addGlowEffect(btn);
            });

            btn.addEventListener('mouseleave', () => {
                this.removeGlowEffect(btn);
            });
        });
    }

    createRippleEffect(e, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    addGlowEffect(element) {
        element.style.boxShadow = '0 0 20px rgba(0, 150, 255, 0.4)';
    }

    removeGlowEffect(element) {
        element.style.boxShadow = '';
    }

    setupFormEnhancements() {
        // Add floating labels effect
        document.querySelectorAll('.glass-input').forEach(input => {
            input.addEventListener('focus', () => {
                this.addInputFocusEffect(input);
            });

            input.addEventListener('blur', () => {
                this.removeInputFocusEffect(input);
            });

            input.addEventListener('input', () => {
                this.validateInputRealTime(input);
            });
        });

        // Setup form validation
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showValidationErrors(form);
                }
            });
        });
    }

    addInputFocusEffect(input) {
        input.style.transform = 'scale(1.02)';
        input.style.boxShadow = '0 0 20px rgba(0, 150, 255, 0.2)';
    }

    removeInputFocusEffect(input) {
        input.style.transform = 'scale(1)';
        if (!input.classList.contains('is-invalid')) {
            input.style.boxShadow = '';
        }
    }

    validateInputRealTime(input) {
        const isValid = this.validateInput(input);
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else if (input.value.length > 0) {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-valid', 'is-invalid');
        }
    }

    validateInput(input) {
        if (input.hasAttribute('required') && !input.value.trim()) {
            return false;
        }

        if (input.type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(input.value);
        }

        if (input.type === 'date') {
            return input.value && new Date(input.value).toString() !== 'Invalid Date';
        }

        if (input.name === 'crm') {
            const crmRegex = /^\d{4,6}-[A-Z]{2}$/;
            return crmRegex.test(input.value);
        }

        return true;
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });

        return isValid;
    }

    showValidationErrors(form) {
        const firstInvalidInput = form.querySelector('.is-invalid');
        if (firstInvalidInput) {
            firstInvalidInput.focus();
            firstInvalidInput.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }

        // Show notification
        this.showNotification('Por favor, corrija os campos destacados.', 'error');
    }

    setupNavigationEnhancements() {
        // Smooth scrolling for internal links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Active navigation highlighting
        this.highlightActiveNavigation();
    }

    highlightActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar .nav-link');

        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    initializeAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe cards and important elements
        document.querySelectorAll('.glass-card, .stat-card, .appointment-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupCounters() {
        const counters = document.querySelectorAll('.counter');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target')) || parseInt(counter.textContent);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += step;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            // Start animation when element is visible
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateCounter();
                        counterObserver.unobserve(entry.target);
                    }
                });
            });

            counterObserver.observe(counter);
        });
    }

    setupNeuralEffects() {
        // Create neural network effect
        this.createNeuralNetwork();
        
        // Add particle effects on interactions
        this.setupParticleEffects();
    }

    createNeuralNetwork() {
        const container = document.querySelector('.neural-bg');
        if (!container) return;

        // Create animated nodes
        for (let i = 0; i < 5; i++) {
            const node = document.createElement('div');
            node.className = 'neural-node';
            node.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: rgba(0, 150, 255, 0.6);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: neuralFloat ${5 + Math.random() * 5}s ease-in-out infinite alternate;
            `;
            container.appendChild(node);
        }
    }

    setupParticleEffects() {
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.createParticleExplosion(e, card);
            });
        });
    }

    createParticleExplosion(e, element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            const angle = (i / 12) * Math.PI * 2;
            const velocity = 50 + Math.random() * 50;
            const size = 2 + Math.random() * 3;

            particle.style.cssText = `
                position: fixed;
                width: ${size}px;
                height: ${size}px;
                background: rgba(0, 150, 255, 0.8);
                border-radius: 50%;
                left: ${centerX}px;
                top: ${centerY}px;
                pointer-events: none;
                z-index: 1000;
                animation: particle 1s ease-out forwards;
                --dx: ${Math.cos(angle) * velocity}px;
                --dy: ${Math.sin(angle) * velocity}px;
            `;

            document.body.appendChild(particle);
            setTimeout(() => particle.remove(), 1000);
        }
    }

    setupLoadingStates() {
        // Add loading states to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    this.showLoadingState(submitBtn);
                }
            });
        });
    }

    showLoadingState(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
        button.disabled = true;
        button.classList.add('loading');

        // Reset after 10 seconds (safety)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.classList.remove('loading');
        }, 10000);
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show neural-notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.5s ease-out;
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.5s ease-out';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }

    // Utility functions
    debounce(func, wait) {
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Global functions for backward compatibility
window.showLoading = function(button) {
    neuralSystem.showLoadingState(button);
};

window.confirmarExclusao = function(message) {
    return confirm(message || 'Tem certeza que deseja excluir este item?');
};

// CSS animations (added dynamically)
const styles = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    @keyframes neuralFloat {
        0% { transform: translateY(0px) translateX(0px); }
        50% { transform: translateY(-20px) translateX(10px); }
        100% { transform: translateY(0px) translateX(-10px); }
    }

    @keyframes particle {
        0% {
            transform: translate(0, 0);
            opacity: 1;
        }
        100% {
            transform: translate(var(--dx), var(--dy));
            opacity: 0;
        }
    }

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

    .neural-notification {
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

// Initialize the neural system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.neuralSystem = new NeuralSystem();
});

// Enhanced form validation for medical forms
class MedicalFormValidator {
    static validateCRM(crm) {
        // Brazilian CRM format: 123456-SP
        const crmRegex = /^\d{4,6}-[A-Z]{2}$/;
        return crmRegex.test(crm);
    }

    static validatePatientName(name) {
        // At least 2 words, each with at least 2 characters
        const nameRegex = /^[A-Za-zÀ-ÿ\s]{2,}\s+[A-Za-zÀ-ÿ\s]{2,}$/;
        return nameRegex.test(name.trim());
    }

    static validateMedication(medication) {
        // Basic medication name validation
        return medication && medication.trim().length >= 3;
    }

    static validateDosage(dosage) {
        // Basic dosage validation
        return dosage && dosage.trim().length >= 2;
    }
}

// Export for global use
window.MedicalFormValidator = MedicalFormValidator;

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.startTime = performance.now();
        this.metrics = {};
    }

    mark(name) {
        this.metrics[name] = performance.now() - this.startTime;
    }

    report() {
        console.log('Neural System Performance Metrics:', this.metrics);
    }
}

window.perfMonitor = new PerformanceMonitor();

// Accessibility enhancements
class AccessibilityEnhancer {
    static init() {
        // Add keyboard navigation
        this.setupKeyboardNavigation();
        
        // Add ARIA labels
        this.setupAriaLabels();
        
        // Add focus management
        this.setupFocusManagement();
    }

    static setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }

    static setupAriaLabels() {
        // Add ARIA labels to buttons without text
        document.querySelectorAll('button:not([aria-label])').forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon && !btn.textContent.trim()) {
                const iconClass = icon.className;
                if (iconClass.includes('fa-plus')) btn.setAttribute('aria-label', 'Adicionar');
                if (iconClass.includes('fa-edit')) btn.setAttribute('aria-label', 'Editar');
                if (iconClass.includes('fa-trash')) btn.setAttribute('aria-label', 'Excluir');
                if (iconClass.includes('fa-search')) btn.setAttribute('aria-label', 'Buscar');
            }
        });
    }

    static setupFocusManagement() {
        // Ensure modals trap focus
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const firstFocusable = modal.querySelector('input, button, select, textarea, [tabindex]');
                if (firstFocusable) firstFocusable.focus();
            });
        });
    }
}

// Initialize accessibility enhancements
document.addEventListener('DOMContentLoaded', () => {
    AccessibilityEnhancer.init();
});
