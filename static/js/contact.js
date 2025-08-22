// Contact form handling

document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    const formMessage = document.getElementById('formMessage');

    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }

    // Real-time validation
    const inputs = contactForm.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearError);
    });
});

async function handleContactSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    // Show loading state
    showLoading(submitBtn);

    try {
        const response = await fetch('/contact', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Thank you! Your message has been sent successfully.', 'success');
            form.reset();
        } else {
            showMessage(data.message || 'An error occurred. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.name;

    clearError(e);

    if (!value) {
        showFieldError(field, getErrorMessage(fieldName, 'required'));
        return false;
    }

    if (field.type === 'email' && !isValidEmail(value)) {
        showFieldError(field, getErrorMessage(fieldName, 'email'));
        return false;
    }

    return true;
}

function clearError(e) {
    const field = e.target;
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.classList.remove('error');
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    let errorDiv = field.parentNode.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-danger small mt-1';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function showMessage(message, type) {
    const formMessage = document.getElementById('formMessage');
    formMessage.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    formMessage.textContent = message;
    formMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        formMessage.style.display = 'none';
    }, 5000);
}

function getErrorMessage(fieldName, errorType) {
    const messages = {
        ar: {
            name: {
                required: 'الاسم مطلوب',
                email: 'البريد الإلكتروني غير صالح'
            },
            email: {
                required: 'البريد الإلكتروني مطلوب',
                email: 'البريد الإلكتروني غير صالح'
            },
            subject: {
                required: 'الموضوع مطلوب'
            },
            message: {
                required: 'الرسالة مطلوبة'
            }
        },
        en: {
            name: {
                required: 'Name is required',
                email: 'Invalid email format'
            },
            email: {
                required: 'Email is required',
                email: 'Invalid email format'
            },
            subject: {
                required: 'Subject is required'
            },
            message: {
                required: 'Message is required'
            }
        }
    };

    const lang = document.documentElement.lang || 'ar';
    return messages[lang][fieldName][errorType];
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>جاري الإرسال...';
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

// Utility functions
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

// Export for global use
window.ContactForm = {
    handleContactSubmit,
    validateField,
    showMessage
};
