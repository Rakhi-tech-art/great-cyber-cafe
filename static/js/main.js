// Main JavaScript for Smart Billing System

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Number formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });
    
    // Dynamic table row addition (for bill items)
    const addRowButton = document.getElementById('addRow');
    if (addRowButton) {
        addRowButton.addEventListener('click', function() {
            const table = document.getElementById('billItemsTable');
            const tbody = table.querySelector('tbody');
            const rowCount = tbody.children.length;
            
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>
                    <input type="text" class="form-control" name="items[${rowCount}][description]" required>
                </td>
                <td>
                    <input type="number" class="form-control quantity" name="items[${rowCount}][quantity]" 
                           value="1" min="0.01" step="0.01" required>
                </td>
                <td>
                    <input type="number" class="form-control rate" name="items[${rowCount}][rate]" 
                           min="0.01" step="0.01" required>
                </td>
                <td>
                    <input type="number" class="form-control total" name="items[${rowCount}][total]" 
                           readonly>
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm remove-row">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(newRow);
            
            // Add event listeners to new row
            addRowEventListeners(newRow);
        });
    }
    
    // Function to add event listeners to table rows
    function addRowEventListeners(row) {
        const quantityInput = row.querySelector('.quantity');
        const rateInput = row.querySelector('.rate');
        const totalInput = row.querySelector('.total');
        const removeButton = row.querySelector('.remove-row');
        
        function calculateTotal() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const rate = parseFloat(rateInput.value) || 0;
            const total = quantity * rate;
            totalInput.value = total.toFixed(2);
            calculateBillTotal();
        }
        
        quantityInput.addEventListener('input', calculateTotal);
        rateInput.addEventListener('input', calculateTotal);
        
        if (removeButton) {
            removeButton.addEventListener('click', function() {
                row.remove();
                calculateBillTotal();
            });
        }
    }
    
    // Add event listeners to existing rows
    const existingRows = document.querySelectorAll('#billItemsTable tbody tr');
    existingRows.forEach(addRowEventListeners);
    
    // Calculate bill total
    function calculateBillTotal() {
        const totalInputs = document.querySelectorAll('.total');
        let subtotal = 0;
        
        totalInputs.forEach(function(input) {
            subtotal += parseFloat(input.value) || 0;
        });
        
        const taxRate = parseFloat(document.getElementById('taxRate')?.value) || 0;
        const discount = parseFloat(document.getElementById('discount')?.value) || 0;
        
        const taxAmount = subtotal * (taxRate / 100);
        const total = subtotal + taxAmount - discount;
        
        if (document.getElementById('subtotal')) {
            document.getElementById('subtotal').value = subtotal.toFixed(2);
        }
        if (document.getElementById('taxAmount')) {
            document.getElementById('taxAmount').value = taxAmount.toFixed(2);
        }
        if (document.getElementById('totalAmount')) {
            document.getElementById('totalAmount').value = total.toFixed(2);
        }
    }
    
    // Tax rate and discount change handlers
    const taxRateInput = document.getElementById('taxRate');
    const discountInput = document.getElementById('discount');
    
    if (taxRateInput) {
        taxRateInput.addEventListener('input', calculateBillTotal);
    }
    if (discountInput) {
        discountInput.addEventListener('input', calculateBillTotal);
    }
    
    // Initialize calculations on page load
    calculateBillTotal();
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}
