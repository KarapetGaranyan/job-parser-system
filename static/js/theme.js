/**
 * Управление темной киберпанк темой
 */

// Глобальная переменная для менеджера темы
let themeManager = null;

// Глобальная функция для переключения темы (доступна сразу)
function toggleTheme() {
    if (themeManager) {
        themeManager.toggleTheme();
    } else {
        // Если менеджер еще не инициализирован, создаем его
        themeManager = new ThemeManager();
        themeManager.toggleTheme();
    }
}

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Применяем сохраненную тему при загрузке
        this.applyTheme(this.currentTheme);
        
        // Обновляем иконку кнопки
        this.updateThemeButton();
        
        // Добавляем обработчик для кнопки
        this.bindEvents();
        
        console.log('ThemeManager инициализирован. Текущая тема:', this.currentTheme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'cyberpunk' : 'light';
        console.log('Переключение темы с', this.currentTheme, 'на', newTheme);
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        this.currentTheme = theme;
        
        // Сохраняем в localStorage
        localStorage.setItem('theme', theme);
        
        // Применяем тему
        this.applyTheme(theme);
        
        // Обновляем кнопку
        this.updateThemeButton();
        
        // Добавляем анимацию переключения
        this.addTransitionEffect();
        
        console.log('Тема установлена:', theme);
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const body = document.body;
        
        if (theme === 'cyberpunk') {
            html.setAttribute('data-theme', 'cyberpunk');
            body.classList.add('cyberpunk-theme');
            console.log('Применена темная тема');
        } else {
            html.removeAttribute('data-theme');
            body.classList.remove('cyberpunk-theme');
            console.log('Применена светлая тема');
        }
    }

    updateThemeButton() {
        const button = document.querySelector('.theme-toggle');
        if (!button) {
            console.warn('Кнопка переключения темы не найдена');
            return;
        }

        const icon = button.querySelector('i');
        const textSpan = button.querySelector('span');

        if (this.currentTheme === 'cyberpunk') {
            // Переключаем на светлую тему
            if (icon) icon.className = 'fas fa-sun me-1';
            if (textSpan) textSpan.textContent = 'Светлая тема';
            button.title = 'Переключить на светлую тему';
        } else {
            // Переключаем на темную тему
            if (icon) icon.className = 'fas fa-moon me-1';
            if (textSpan) textSpan.textContent = 'Темная тема';
            button.title = 'Переключить на темную тему';
        }
        
        console.log('Кнопка обновлена для темы:', this.currentTheme);
    }

    addTransitionEffect() {
        // Добавляем класс для плавного перехода
        document.body.classList.add('theme-transitioning');
        
        // Убираем класс через время анимации
        setTimeout(() => {
            document.body.classList.remove('theme-transitioning');
        }, 300);
    }

    bindEvents() {
        // Обработчик для кнопки переключения темы
        const button = document.querySelector('.theme-toggle');
        if (button) {
            // Удаляем старый обработчик, если есть
            button.removeEventListener('click', this.handleButtonClick);
            
            // Добавляем новый обработчик
            this.handleButtonClick = (e) => {
                e.preventDefault();
                console.log('Кнопка темы нажата');
                this.toggleTheme();
            };
            
            button.addEventListener('click', this.handleButtonClick);
            console.log('Обработчик кнопки добавлен');
        } else {
            console.warn('Кнопка переключения темы не найдена для привязки событий');
        }

        // Обработчик клавиши для быстрого переключения (Ctrl+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                console.log('Горячая клавиша Ctrl+T нажата');
                this.toggleTheme();
            }
        });
    }

    // Метод для получения текущей темы
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Метод для проверки, активна ли темная тема
    isDarkTheme() {
        return this.currentTheme === 'cyberpunk';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен, инициализируем ThemeManager');
    
    // Создаем глобальный экземпляр
    themeManager = new ThemeManager();
    window.themeManager = themeManager;
    
    // Добавляем CSS для плавных переходов
    const style = document.createElement('style');
    style.textContent = `
        .theme-transitioning * {
            transition: all 0.3s ease !important;
        }
        
        /* Дополнительные стили для плавного перехода */
        body {
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .navbar, .card, .btn, .form-control, .alert, .table {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
    
    console.log('ThemeManager готов к работе');
});

// Дополнительная инициализация для случаев, когда DOM уже загружен
if (document.readyState === 'loading') {
    // DOM еще загружается
    console.log('DOM загружается, ждем...');
} else {
    // DOM уже загружен
    console.log('DOM уже загружен, инициализируем немедленно');
    if (!themeManager) {
        themeManager = new ThemeManager();
        window.themeManager = themeManager;
    }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
} 