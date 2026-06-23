/**
 * CampusDeck - Interactive Client Logic Script
 * Handles theme toggles, mobile sidebar navigation, sticky note indicators,
 * deadline countdowns, flash notifications, delete confirmations, and dashboard components.
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. Theme Toggle (Light/Dark Mode)
    // =========================================================================
    const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
    
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        if (theme === 'light') {
            themeToggleBtns.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-moon"></i>';
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
            });
        } else {
            themeToggleBtns.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-sun"></i>';
                btn.setAttribute('aria-label', 'Switch to Light Mode');
            });
        }
    };

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    themeToggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    });

    // =========================================================================
    // 2. Mobile Sidebar Navigation Toggle
    // =========================================================================
    const sidebar = document.getElementById('app-sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.add('open');
            if (sidebarOverlay) sidebarOverlay.classList.add('open');
        });
    }

    if (sidebar && sidebarClose) {
        sidebarClose.addEventListener('click', () => {
            sidebar.classList.remove('open');
            if (sidebarOverlay) sidebarOverlay.classList.remove('open');
        });
    }

    if (sidebar && sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('open');
        });
    }

    // =========================================================================
    // 3. Client-Side Deadline Calculators
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
            badgeText = `${diffDays} d left`;
            badgeClass = 'urgent';
        } else if (diffDays <= 7) {
            badgeText = `${diffDays} d left`;
            badgeClass = 'soon';
        } else {
            badgeText = `${diffDays} d left`;
            badgeClass = 'safe';
        }

        const pill = elem.querySelector('.days-left');
        if (pill) {
            pill.textContent = badgeText;
            pill.className = `days-left ${badgeClass}`;
        }
    });

    // =========================================================================
    // 4. Flash Alert Message Autohide & Closing
    // =========================================================================
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                flash.remove();
            }, 400);
        }, 4000);

        const closeBtn = flash.querySelector('.btn-close-flash');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                flash.remove();
            });
        }
    });

    // =========================================================================
    // 5. Delete Action Confirmation dialogs
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
    // 6. Auto-populate Empty Dates
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
    // 7. Dashboard Welcome greetings & Metric Animations
    // =========================================================================
    const greetingEl = document.getElementById('dashboard-greeting');

    if (greetingEl) {
        // Set dynamic contextual greeting
        const updateGreeting = () => {
            const now = new Date();
            const hour = now.getHours();
            const userName = greetingEl.getAttribute('data-username') || 'Student';
            let greeting = '';
            
            if (hour >= 5 && hour < 12) {
                greeting = `Good morning, ${userName} ☀️`;
            } else if (hour >= 12 && hour < 17) {
                greeting = `Good afternoon, ${userName} 👋`;
            } else if (hour >= 17 && hour < 22) {
                greeting = `Good evening, ${userName} 🌙`;
            } else {
                greeting = `Late night study, ${userName}? 🌙`;
            }
            
            if (greetingEl.textContent !== greeting) {
                greetingEl.textContent = greeting;
            }
        };

        // Call immediately and set interval for dynamic greeting
        updateGreeting();
        setInterval(updateGreeting, 60000);
    }

    // Progress Bar and Circular Ring load-in animations on Dashboard
    const gpaBar = document.getElementById('dashboard-gpa-bar');
    if (gpaBar) {
        const gpaValue = parseFloat(gpaBar.getAttribute('data-gpa')) || 0.0;
        const percentage = Math.min(Math.max((gpaValue / 10.0) * 100, 0), 100);
        setTimeout(() => {
            gpaBar.style.width = `${percentage}%`;
        }, 150);
    }

    const gpaCircle = document.getElementById('gpa-progress-circle');
    if (gpaCircle) {
        const targetOffset = parseFloat(gpaCircle.getAttribute('data-offset')) || 0.0;
        setTimeout(() => {
            gpaCircle.style.strokeDashoffset = targetOffset;
        }, 150);
    }

    // =========================================================================
    // 8. Scroll Reveal Animation for Dashboard Cards
    // =========================================================================
    const revealElements = document.querySelectorAll('.scroll-reveal');
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null,
        threshold: 0.1,
        rootMargin: "0px 0px -20px 0px"
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // =========================================================================
    // 9. Goals Filtering Logic
    // =========================================================================
    const goalFilterBtns = document.querySelectorAll('.filter-goal-btn');
    const goalCards = document.querySelectorAll('.goal-card');

    if (goalFilterBtns.length > 0 && goalCards.length > 0) {
        goalFilterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class
                goalFilterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const filterValue = btn.getAttribute('data-filter');
                
                goalCards.forEach(card => {
                    if (filterValue === 'All' || card.getAttribute('data-priority') === filterValue) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // =========================================================================
    // 10. Opportunities Filtering Logic
    // =========================================================================
    const oppFilterBtns = document.querySelectorAll('.filter-opp-btn');
    const oppCards = document.querySelectorAll('.opportunity-card');

    if (oppFilterBtns.length > 0 && oppCards.length > 0) {
        oppFilterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                oppFilterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const filterValue = btn.getAttribute('data-filter');
                
                oppCards.forEach(card => {
                    if (filterValue === 'All' || card.getAttribute('data-category') === filterValue) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // =========================================================================
    // 11. Calendar Generation Logic
    // =========================================================================
    const calendarGrid = document.getElementById('calendar-grid');
    const monthYearText = document.getElementById('calendar-month-year');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');

    if (calendarGrid && window.calendarData) {
        let currentDate = new Date();
        
        const renderCalendar = () => {
            calendarGrid.innerHTML = '';
            
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            
            // Format Title
            const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            monthYearText.textContent = `${monthNames[month]} ${year}`;
            
            // Get first day of month and total days
            const firstDay = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            
            // Generate empty slots for previous month
            for (let i = 0; i < firstDay; i++) {
                const emptyCell = document.createElement('div');
                emptyCell.className = 'calendar-day empty';
                calendarGrid.appendChild(emptyCell);
            }
            
            // Generate days
            const today = new Date();
            const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month;
            
            for (let day = 1; day <= daysInMonth; day++) {
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day';
                if (isCurrentMonth && day === today.getDate()) {
                    dayCell.classList.add('today');
                }
                
                const dayNum = document.createElement('span');
                dayNum.className = 'day-number';
                dayNum.textContent = day;
                dayCell.appendChild(dayNum);
                
                // Format date string as YYYY-MM-DD
                const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                
                // Add Goals
                window.calendarData.goals.forEach(goal => {
                    if (goal.target_date === dateString) {
                        const eventDiv = document.createElement('div');
                        let priorityClass = 'cal-medium';
                        if (goal.priority === 'High') priorityClass = 'cal-high';
                        if (goal.priority === 'Low') priorityClass = 'cal-low';
                        if (goal.status === 'Completed') priorityClass = 'cal-completed';
                        
                        eventDiv.className = `calendar-event ${priorityClass}`;
                        eventDiv.textContent = `🎯 ${goal.title}`;
                        eventDiv.title = goal.title;
                        dayCell.appendChild(eventDiv);
                    }
                });
                
                // Add Opportunities
                window.calendarData.opportunities.forEach(opp => {
                    if (opp.deadline === dateString) {
                        const eventDiv = document.createElement('div');
                        let catClass = 'cal-event';
                        if (opp.category === 'Hackathons') catClass = 'cal-hackathon';
                        if (opp.category === 'Internships') catClass = 'cal-internship';
                        if (opp.status === 'Completed') catClass = 'cal-completed';
                        
                        eventDiv.className = `calendar-event ${catClass}`;
                        eventDiv.textContent = `💼 ${opp.name}`;
                        eventDiv.title = opp.name;
                        dayCell.appendChild(eventDiv);
                    }
                });
                
                calendarGrid.appendChild(dayCell);
            }
            
            // Fill remaining grid spaces
            const totalCells = firstDay + daysInMonth;
            const remainingCells = 42 - totalCells; // 6 rows max
            for (let i = 0; i < remainingCells; i++) {
                if (totalCells + i > 35 && remainingCells > 7) continue; 
                const emptyCell = document.createElement('div');
                emptyCell.className = 'calendar-day empty';
                calendarGrid.appendChild(emptyCell);
            }
        };

        renderCalendar();

        prevMonthBtn.addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            renderCalendar();
        });

        nextMonthBtn.addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            renderCalendar();
        });
    }
});
