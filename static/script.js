/**
 * CampusDeck - Interactive Client Logic Script
 * Handles theme toggles, mobile navigation, sticky note rotation, deadline countdowns,
 * flash notifications, and animated dashboard components (live clock, greetings, progress loaders).
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. Theme Toggle (Light/Dark Mode)
    // =========================================================================
    const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
    
    const applyTheme = (theme) => {
        if (theme === 'light') {
            document.body.classList.add('light-mode');
            themeToggleBtns.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-moon"></i>';
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
            });
        } else {
            document.body.classList.remove('light-mode');
            themeToggleBtns.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-sun"></i>';
                btn.setAttribute('aria-label', 'Switch to Light Mode');
            });
        }
    };

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        applyTheme('dark');
    }

    themeToggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const isLight = document.body.classList.contains('light-mode');
            const newTheme = isLight ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    });

    // =========================================================================
    // 2. Mobile Navigation Toggle
    // =========================================================================
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (icon) {
                if (navLinks.classList.contains('active')) {
                    icon.className = 'fas fa-times';
                } else {
                    icon.className = 'fas fa-bars';
                }
            }
        });
    }

    // =========================================================================
    // 3. Active Nav Menu Underlining/Highlighting
    // =========================================================================
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-links li');
    navItems.forEach(item => {
        const link = item.querySelector('a');
        if (link) {
            const href = link.getAttribute('href');
            if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        }
    });

    // =========================================================================
    // 4. Random Rotation for Pinned Sticky Notes
    // =========================================================================
    const stickyNotes = document.querySelectorAll('.sticky-note');
    stickyNotes.forEach(note => {
        const randomRotate = (Math.random() * 6 - 3).toFixed(1);
        note.style.setProperty('--rotation', `${randomRotate}deg`);
    });

    // =========================================================================
    // 5. Client-Side Deadline Calculators
    // =========================================================================
    const deadlineElements = document.querySelectorAll('[data-deadline]');
    deadlineElements.forEach(elem => {
        const deadlineStr = elem.getAttribute('data-deadline');
        if (!deadlineStr) return;

        const deadlineDate = new Date(deadlineStr);
        deadlineDate.setHours(23, 59, 59, 999);
        const today = new Date();
        
        const diffTime = deadlineDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        let badgeText = '';
        let badgeClass = '';

        if (diffDays < 0) {
            badgeText = 'Overdue';
            badgeClass = 'urgent';
        } else if (diffDays === 0) {
            badgeText = 'Today';
            badgeClass = 'urgent';
        } else if (diffDays === 1) {
            badgeText = 'Tomorrow';
            badgeClass = 'urgent';
        } else if (diffDays <= 3) {
            badgeText = `${diffDays} days left`;
            badgeClass = 'urgent';
        } else if (diffDays <= 7) {
            badgeText = `${diffDays} days left`;
            badgeClass = 'soon';
        } else {
            badgeText = `${diffDays} days left`;
            badgeClass = 'safe';
        }

        const pill = elem.querySelector('.days-left');
        if (pill) {
            pill.textContent = badgeText;
            pill.className = `days-left ${badgeClass}`;
        }
    });

    // =========================================================================
    // 6. Flash Alert Message Autohide & Closing
    // =========================================================================
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                flash.remove();
            }, 500);
        }, 4000);

        const closeBtn = flash.querySelector('.btn-close-flash');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                flash.remove();
            });
        }
    });

    // =========================================================================
    // 7. Delete Action Confirmation dialogs
    // =========================================================================
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmed = confirm('Are you sure you want to permanently delete this item?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // =========================================================================
    // 8. Auto-populate Empty Dates
    // =========================================================================
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            input.value = `${year}-${month}-${day}`;
        }
    });

    // =========================================================================
    // 9. Dashboard Welcome greetings, Live Clock, & Metric Animations
    // =========================================================================
    const clockEl = document.getElementById('dashboard-clock');
    const greetingEl = document.getElementById('dashboard-greeting');

    if (clockEl || greetingEl) {
        // Set dynamic contextual greeting and run live clock updates
        const updateClockAndGreeting = () => {
            const now = new Date();
            
            // Format Clock: hh:mm:ss AM/PM
            if (clockEl) {
                let hours = now.getHours();
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12; // conversion of '0' hour to '12'
                const displayHours = String(hours).padStart(2, '0');
                clockEl.textContent = `⏰ ${displayHours}:${minutes}:${seconds} ${ampm}`;
            }

            // Update Greeting Context
            if (greetingEl) {
                const hour = now.getHours();
                const userName = greetingEl.getAttribute('data-username') || 'Student';
                let greeting = '';
                
                if (hour >= 5 && hour < 12) {
                    greeting = `Good morning, ${userName}! 👋`;
                } else if (hour >= 12 && hour < 17) {
                    greeting = `Good afternoon, ${userName}! 👋`;
                } else if (hour >= 17 && hour < 22) {
                    greeting = `Good evening, ${userName}! 👋`;
                } else {
                    greeting = `Late night study, ${userName}? 🌙`;
                }
                
                if (greetingEl.textContent !== greeting) {
                    greetingEl.textContent = greeting;
                }
            }
        };

        // Call immediately and set interval for ticking clock
        updateClockAndGreeting();
        setInterval(updateClockAndGreeting, 1000);
    }

    // Progress Bar load-in animations on Dashboard
    const gpaBar = document.getElementById('dashboard-gpa-bar');
    if (gpaBar) {
        const gpaValue = parseFloat(gpaBar.getAttribute('data-gpa')) || 0.0;
        // Scaled to a 10.0 scale: percentage is (gpaValue / 10) * 100
        const percentage = Math.min(Math.max((gpaValue / 10.0) * 100, 0), 100);
        setTimeout(() => {
            gpaBar.style.width = `${percentage}%`;
        }, 150);
    }
});
