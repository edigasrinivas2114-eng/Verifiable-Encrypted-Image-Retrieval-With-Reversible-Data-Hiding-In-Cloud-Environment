// Simple UploadImage JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file_upload');
    const filePreviewSection = document.getElementById('filePreviewSection');
    const previewImage = document.getElementById('previewImage');
    const selectedFileName = document.getElementById('selectedFileName');
    const fileSize = document.getElementById('fileSize');
    const uploadBtn = document.getElementById('uploadBtn');
    const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));

    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            
            // Show file info
            selectedFileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                filePreviewSection.style.display = 'block';
                uploadBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    // Check if there's a data message on page load and show popup
    function checkForDataMessage() {
        const alertMessage = document.querySelector('.alert-message');
        if (alertMessage) {
            const message = alertMessage.textContent;
            if (message.includes('Encrypted image outsource')) {
                // Extract verification code
                const codeMatch = message.match(/verification code = ([a-f0-9]+)/);
                const verificationCode = codeMatch ? codeMatch[1] : 'N/A';
                
                // Get filename from the form or use a default
                const fileName = fileInput.files[0] ? fileInput.files[0].name : 'Uploaded Image';
                
                // Show success popup
                showSuccessPopup(verificationCode, fileName);
                
                // Hide the alert message since we're showing the popup
                alertMessage.style.display = 'none';
            }
        }
    }

    // Check for data message on page load
    checkForDataMessage();

    function showSuccessPopup(verificationCode, fileName) {
        // Update modal content
        document.getElementById('verificationCode').textContent = verificationCode;
        document.getElementById('userName').textContent = 'Current User';
        document.getElementById('uploadDate').textContent = new Date().toLocaleDateString();
        document.getElementById('uploadedFileName').textContent = fileName;
        
        // Show modal
        resultModal.show();
        
        // Clear file selection
        clearFile();
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Global functions
    window.clearFile = function() {
        fileInput.value = '';
        filePreviewSection.style.display = 'none';
        uploadBtn.disabled = true;
    };

    window.copyToClipboard = function() {
        const code = document.getElementById('verificationCode').textContent;
        navigator.clipboard.writeText(code).then(() => {
            alert('Verification code copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy to clipboard');
        });
    };

    window.uploadAnother = function() {
        resultModal.hide();
        clearFile();
    };
});