// معالجة نموذج المشاريع مع رفع الصور المتعددة

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('projectForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const additionalImagesInput = document.getElementById('additional_images');
    const imagePreview = document.getElementById('imagePreview');
    
    // معاينة الصور قبل الرفع
    if (additionalImagesInput) {
        additionalImagesInput.addEventListener('change', handleImagePreview);
    }
    
    // معالجة حذف الصور الحالية
    document.querySelectorAll('.btn-delete-image').forEach(button => {
        button.addEventListener('click', function() {
            const imageId = this.getAttribute('data-image-id');
            if (confirm('هل أنت متأكد من حذف هذه الصورة؟')) {
                deleteImage(imageId, this);
            }
        });
    });
    
    // معالجة إرسال النموذج
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

// معالجة معاينة الصور
function handleImagePreview(event) {
    const files = event.target.files;
    const previewContainer = document.getElementById('imagePreview');
    
    if (files.length > 0) {
        previewContainer.style.display = 'block';
        previewContainer.innerHTML = '<h6>معاينة الصور الجديدة:</h6>';
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const col = document.createElement('div');
                    col.className = 'col-md-3 mb-3';
                    col.innerHTML = `
                        <div class="card">
                            <img src="${e.target.result}" class="card-img-top" alt="Preview">
                            <div class="card-body p-2">
                                <small class="text-muted">${file.name}</small>
                            </div>
                        </div>
                    `;
                    previewContainer.appendChild(col);
                };
                reader.readAsDataURL(file);
            }
        }
    } else {
        previewContainer.style.display = 'none';
    }
}

// معالجة إرسال النموذج مع شريط التحميل
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // إظهار شريط التحميل
    showProgress();
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // إعادة توجيه بعد النجاح
            window.location.href = response.url;
        } else {
            throw new Error('فشل في رفع البيانات');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء رفع البيانات. يرجى المحاولة مرة أخرى.');
        hideProgress();
    }
}

// إظهار شريط التحميل
function showProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    progressContainer.style.display = 'block';
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 90) {
            progress = 90;
            clearInterval(interval);
        }
        
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';
        progressText.textContent = `جاري رفع الصور... ${Math.round(progress)}%`;
    }, 200);
}

// إخفاء شريط التحميل
function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    progressContainer.style.display = 'none';
}

// حذف صورة من المشروع
async function deleteImage(imageId, button) {
    try {
        const response = await fetch(`/admin/project/image/delete/${imageId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // إزالة عنصر الصورة من DOM
            const card = button.closest('.col-md-3');
            card.remove();
            flash('تم حذف الصورة بنجاح', 'success');
        } else {
            throw new Error('فشل في حذف الصورة');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء حذف الصورة. يرجى المحاولة مرة أخرى.');
    }
}

// دالة لعرض رسائل التنبيه
function flash(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// التحقق من صحة النموذج
(function() {
    'use strict';
    
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
})();
