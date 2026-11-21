// Interactive JS utilities for Employee Management System (EMS)

document.addEventListener('DOMContentLoaded', function () {
    // 1. Sidebar Toggle Functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarWrapper = document.getElementById('sidebar-wrapper');

    if (sidebarToggle && sidebarWrapper) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            if (sidebarWrapper.style.display === 'none') {
                sidebarWrapper.style.display = 'block';
            } else if (window.innerWidth < 768) {
                sidebarWrapper.style.display = sidebarWrapper.style.display === 'block' ? 'none' : 'block';
            }
        });
    }

    // 2. Live Salary Calculation: Net Salary = Basic + Allowances - Deductions
    const basicInput = document.getElementById('id_basic_salary');
    const allowancesInput = document.getElementById('id_allowances');
    const deductionsInput = document.getElementById('id_deductions');
    const netSalaryDisplay = document.getElementById('netSalaryLiveDisplay');

    function calculateNetSalary() {
        if (basicInput) {
            const basic = parseFloat(basicInput.value) || 0;
            const allowances = allowancesInput ? (parseFloat(allowancesInput.value) || 0) : 0;
            const deductions = deductionsInput ? (parseFloat(deductionsInput.value) || 0) : 0;

            const netSalary = Math.max(0, basic + allowances - deductions);
            if (netSalaryDisplay) {
                netSalaryDisplay.innerText = netSalary.toLocaleString('en-IN', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        }
    }

    if (basicInput) {
        basicInput.addEventListener('input', calculateNetSalary);
        if (allowancesInput) allowancesInput.addEventListener('input', calculateNetSalary);
        if (deductionsInput) deductionsInput.addEventListener('input', calculateNetSalary);
        // Initial run
        calculateNetSalary();
    }

    // 3. Auto dismiss bootstrap alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 6000);
    });

    // 4. Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
