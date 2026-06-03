// Graph Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initializeAnimations();
    
    // Initialize graph interactions
    initializeGraphInteractions();
    
    // Initialize performance indicators
    initializePerformanceIndicators();
});

// Initialize animations
function initializeAnimations() {
    // Add staggered animation to analysis cards
    const analysisCards = document.querySelectorAll('.analysis-card');
    analysisCards.forEach((card, index) => {
        card.style.animationDelay = `${0.1 * index}s`;
        card.classList.add('animate__animated', 'animate__fadeInUp');
    });
    
    // Add animation to graph image
    const graphImage = document.querySelector('.graph-image');
    if (graphImage) {
        graphImage.classList.add('animate__animated', 'animate__zoomIn');
        graphImage.style.animationDelay = '0.5s';
    }
}

// Initialize graph interactions
function initializeGraphInteractions() {
    const graphImage = document.querySelector('.graph-image');
    if (graphImage) {
        // Add click to zoom functionality
        graphImage.addEventListener('click', function() {
            openImageModal(this.src, this.alt);
        });
        
        // Add hover effects
        graphImage.addEventListener('mouseenter', function() {
            this.style.cursor = 'zoom-in';
        });
    }
}

// Initialize performance indicators
function initializePerformanceIndicators() {
    const indicators = document.querySelectorAll('.indicator-value');
    indicators.forEach(indicator => {
        // Add pulse animation for outstanding performance
        if (indicator.classList.contains('outstanding')) {
            indicator.style.animation = 'pulse 2s infinite';
        }
    });
}

// Download graph function
function downloadGraph() {
    const graphImage = document.querySelector('.graph-image');
    if (graphImage) {
        const link = document.createElement('a');
        link.download = 'performance-graph.png';
        link.href = graphImage.src;
        link.click();
        
        // Show success message
        showNotification('Graph downloaded successfully!', 'success');
    }
}

// Print graph function
function printGraph() {
    const graphImage = document.querySelector('.graph-image');
    if (graphImage) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Performance Graph</title>
                    <style>
                        body { 
                            margin: 0; 
                            padding: 20px; 
                            text-align: center; 
                            font-family: Arial, sans-serif;
                        }
                        img { 
                            max-width: 100%; 
                            height: auto; 
                            border: 1px solid #ddd;
                            border-radius: 8px;
                        }
                        h1 { 
                            color: #333; 
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Performance Analytics Graph</h1>
                    <img src="${graphImage.src}" alt="Performance Graph">
                    <p>Generated on ${new Date().toLocaleDateString()}</p>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        
        // Show success message
        showNotification('Print dialog opened!', 'info');
    }
}

// Open image modal for zoom functionality
function openImageModal(imageSrc, imageAlt) {
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="imageModalLabel">${imageAlt}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageSrc}" alt="${imageAlt}" class="img-fluid">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="downloadGraph()">
                            <i class="fas fa-download"></i> Download
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('imageModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('imageModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Add smooth scrolling for any anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading state to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function() {
        if (this.type === 'submit' || this.onclick) {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            this.disabled = true;
            
            // Re-enable after 2 seconds (adjust as needed)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        }
    });
});

// Add intersection observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate__animated', 'animate__fadeInUp');
        }
    });
}, observerOptions);

// Observe elements for scroll animations
document.querySelectorAll('.analysis-card, .graph-display-section').forEach(el => {
    observer.observe(el);
});

