// Beautiful Form Interactions and Enhancements
document.addEventListener('DOMContentLoaded', function() {
    
    // Form validation and enhancement
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add loading state to submit buttons
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('.submit-btn');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Re-enable after 3 seconds (in case of errors)
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
        
        // Real-time input validation
        const inputs = form.querySelectorAll('.form-input');
        inputs.forEach(input => {
            // Add focus/blur effects
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                validateInput(this);
            });
            
            // Real-time validation
            input.addEventListener('input', function() {
                validateInput(this);
            });
        });
    });
    
    // Input validation function
    function validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        const name = input.name;
        
        // Remove previous validation classes
        input.classList.remove('error', 'success');
        
        // Basic validation
        if (value === '') {
            if (input.required) {
                input.classList.add('error');
                return false;
            }
            return true;
        }
        
        // Type-specific validation
        let isValid = true;
        
        switch (type) {
            case 'email':
                isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
                break;
            case 'tel':
                isValid = /^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/\s/g, ''));
                break;
            case 'password':
                isValid = value.length >= 6;
                break;
            case 'text':
                if (name === 'username') {
                    isValid = value.length >= 3 && /^[a-zA-Z0-9_]+$/.test(value);
                }
                break;
        }
        
        if (isValid) {
            input.classList.add('success');
        } else {
            input.classList.add('error');
        }
        
        return isValid;
    }
    
    // File upload enhancement
    const fileInputs = document.querySelectorAll('.file-upload-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const label = this.closest('.file-upload-label');
            const text = label.querySelector('.file-upload-text');
            const icon = label.querySelector('.file-upload-icon');
            
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                text.textContent = fileName;
                icon.className = 'file-upload-icon fas fa-check-circle';
                label.style.borderColor = '#28a745';
                label.style.background = 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)';
            }
        });
    });
    
    // Smooth scroll for form navigation
    const formLinks = document.querySelectorAll('a[href^="/"]');
    formLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').includes('UserLogin') || 
                this.getAttribute('href').includes('Register')) {
                e.preventDefault();
                const targetUrl = this.getAttribute('href');
                
                // Add fade out effect
                document.body.style.opacity = '0.8';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 300);
            }
        });
    });
    
    // Auto-hide alert messages
    const alertMessages = document.querySelectorAll('.alert-message');
    alertMessages.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            alert.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.submit-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        .submit-btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .form-field.focused .input-icon {
            color: #0056b3;
            transform: translateY(-50%) scale(1.1);
        }
    `;
    document.head.appendChild(style);
    
    // Form submission feedback
    const formContainers = document.querySelectorAll('.form-container');
    formContainers.forEach(container => {
        const form = container.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                // Add success animation
                container.style.transform = 'scale(0.98)';
                container.style.transition = 'transform 0.2s ease';
                
                setTimeout(() => {
                    container.style.transform = 'scale(1)';
                }, 200);
            });
        }
    });
    
    // Keyboard navigation enhancement
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.classList.contains('form-input')) {
            const form = e.target.closest('form');
            if (form) {
                const inputs = Array.from(form.querySelectorAll('.form-input'));
                const currentIndex = inputs.indexOf(e.target);
                const nextInput = inputs[currentIndex + 1];
                
                if (nextInput) {
                    e.preventDefault();
                    nextInput.focus();
                } else {
                    // Submit form if it's the last input
                    const submitBtn = form.querySelector('.submit-btn');
                    if (submitBtn) {
                        e.preventDefault();
                        submitBtn.click();
                    }
                }
            }
        }
    });
    
    console.log('🎨 Beautiful form interactions loaded successfully!');
});

