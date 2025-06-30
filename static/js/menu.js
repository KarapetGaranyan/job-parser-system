/**
 * Интерактивное меню для Job Parser System
 */

class MenuManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupMenuEffects();
        this.setupActiveLinks();
        this.setupDropdownEffects();
        this.setupMobileMenu();
        this.setupScrollEffects();
    }

    setupMenuEffects() {
        // Эффект при наведении на пункты меню
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', (e) => {
                this.addHoverEffect(e.target);
            });
            
            link.addEventListener('mouseleave', (e) => {
                this.removeHoverEffect(e.target);
            });
        });
    }

    addHoverEffect(element) {
        // Добавляем класс для анимации
        element.classList.add('menu-hover');
        
        // Эффект пульсации для иконок
        const icon = element.querySelector('i');
        if (icon) {
            icon.style.animation = 'pulse 0.6s ease-in-out';
        }
    }

    removeHoverEffect(element) {
        element.classList.remove('menu-hover');
        
        const icon = element.querySelector('i');
        if (icon) {
            icon.style.animation = '';
        }
    }

    setupActiveLinks() {
        // Подсвечиваем активную ссылку
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
                
                // Добавляем эффект для активной ссылки
                this.addActiveEffect(link);
            }
        });
    }

    addActiveEffect(element) {
        // Добавляем пульсирующий эффект для активной ссылки
        element.style.animation = 'pulse 2s infinite';
        
        // Добавляем градиентную рамку
        element.style.border = '2px solid transparent';
        element.style.backgroundImage = 'linear-gradient(white, white), linear-gradient(45deg, #667eea, #764ba2)';
        element.style.backgroundOrigin = 'border-box';
        element.style.backgroundClip = 'content-box, border-box';
    }

    setupDropdownEffects() {
        // Эффекты для выпадающих меню
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (toggle && menu) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleDropdown(dropdown, menu);
                });
            }
        });
    }

    toggleDropdown(dropdown, menu) {
        const isOpen = dropdown.classList.contains('show');
        
        // Закрываем все другие дропдауны
        document.querySelectorAll('.dropdown.show').forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('show');
                d.querySelector('.dropdown-menu').classList.remove('show');
            }
        });
        
        if (!isOpen) {
            dropdown.classList.add('show');
            menu.classList.add('show');
            
            // Анимация появления
            menu.style.animation = 'slideInDown 0.3s ease';
        } else {
            dropdown.classList.remove('show');
            menu.classList.remove('show');
        }
    }

    setupMobileMenu() {
        // Эффекты для мобильного меню
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', () => {
                this.toggleMobileMenu(navbarCollapse);
            });
        }
    }

    toggleMobileMenu(collapse) {
        const isOpen = collapse.classList.contains('show');
        
        if (!isOpen) {
            collapse.classList.add('show');
            collapse.style.animation = 'slideInDown 0.4s ease';
        } else {
            collapse.classList.remove('show');
        }
    }

    setupScrollEffects() {
        // Эффекты при прокрутке
        let lastScrollTop = 0;
        
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Прокрутка вниз - скрываем меню
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Прокрутка вверх - показываем меню
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        });
    }

    // Метод для добавления уведомлений в меню
    addNotification(element, count = 1) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-danger position-absolute top-0 start-100 translate-middle';
        badge.textContent = count;
        badge.style.fontSize = '0.6rem';
        badge.style.padding = '2px 4px';
        
        element.style.position = 'relative';
        element.appendChild(badge);
        
        // Анимация появления
        badge.style.animation = 'pulse 1s ease-in-out';
    }

    // Метод для удаления уведомлений
    removeNotification(element) {
        const badge = element.querySelector('.badge');
        if (badge) {
            badge.remove();
        }
    }

    // Метод для добавления эффекта загрузки
    addLoadingEffect(element) {
        const spinner = document.createElement('i');
        spinner.className = 'fas fa-spinner fa-spin ms-1';
        spinner.style.fontSize = '0.8em';
        
        element.appendChild(spinner);
        
        return () => {
            spinner.remove();
        };
    }
}

// Инициализация менеджера меню
document.addEventListener('DOMContentLoaded', function() {
    window.menuManager = new MenuManager();
    
    // Добавляем глобальные обработчики
    document.addEventListener('click', function(e) {
        // Закрываем дропдауны при клике вне их
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.show').forEach(dropdown => {
                dropdown.classList.remove('show');
                dropdown.querySelector('.dropdown-menu').classList.remove('show');
            });
        }
    });
    
    // Эффект для кнопки бренда
    const brand = document.querySelector('.navbar-brand');
    if (brand) {
        brand.addEventListener('click', function() {
            this.style.animation = 'wave 0.6s ease-in-out';
            setTimeout(() => {
                this.style.animation = '';
            }, 600);
        });
    }
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MenuManager;
} 