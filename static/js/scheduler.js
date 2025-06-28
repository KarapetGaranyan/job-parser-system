class SchedulerManager {
    constructor() {
        this.statusCheckInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStatus();
        this.startAutoRefresh();
    }

    bindEvents() {
        document.getElementById('startSchedulerBtn').addEventListener('click', () => this.startScheduler());
        document.getElementById('stopSchedulerBtn').addEventListener('click', () => this.stopScheduler());
        document.getElementById('refreshStatusBtn').addEventListener('click', () => this.loadStatus());
    }

    async startScheduler() {
        this.setButtonLoading('startSchedulerBtn', true);

        try {
            const response = await fetch('/api/scheduler/start', { method: 'POST' });
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.showMessage('✅ Планировщик запущен успешно', 'success');
            setTimeout(() => this.loadStatus(), 1000);

        } catch (error) {
            this.showMessage('❌ Ошибка запуска: ' + error.message, 'danger');
        } finally {
            this.setButtonLoading('startSchedulerBtn', false);
        }
    }

    async stopScheduler() {
        if (!confirm('⚠️ Остановить планировщик? Все автоматические задачи будут прекращены.')) {
            return;
        }

        this.setButtonLoading('stopSchedulerBtn', true);

        try {
            const response = await fetch('/api/scheduler/stop', { method: 'POST' });
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.showMessage('⏹️ Планировщик остановлен', 'warning');
            setTimeout(() => this.loadStatus(), 1000);

        } catch (error) {
            this.showMessage('❌ Ошибка остановки: ' + error.message, 'danger');
        } finally {
            this.setButtonLoading('stopSchedulerBtn', false);
        }
    }

    async loadStatus() {
        this.setButtonLoading('refreshStatusBtn', true);

        try {
            const response = await fetch('/api/scheduler/status');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayStatus(data);
            this.displayJobs(data.jobs || {});

        } catch (error) {
            this.showError('Ошибка загрузки статуса: ' + error.message);
        } finally {
            this.setButtonLoading('refreshStatusBtn', false);
        }
    }

    displayStatus(data) {
        const container = document.getElementById('schedulerStatus');
        const isRunning = data.running;
        const jobsCount = Object.keys(data.jobs || {}).length;

        const statusClass = isRunning ? 'alert-success' : 'alert-warning';
        const statusIcon = isRunning ? '🟢' : '🔴';
        const statusText = isRunning ? 'Работает' : 'Остановлен';

        container.className = `alert ${statusClass}`;
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${statusIcon} Статус: ${statusText}</h6>
                    <small>Активных задач: ${jobsCount}</small>
                </div>
                <div class="text-end">
                    <small class="text-muted">Последняя проверка: ${new Date().toLocaleTimeString('ru-RU')}</small>
                </div>
            </div>
        `;

        // Обновляем состояние кнопок
        document.getElementById('startSchedulerBtn').disabled = isRunning;
        document.getElementById('stopSchedulerBtn').disabled = !isRunning;
    }

    displayJobs(jobs) {
        const container = document.getElementById('jobsList');

        if (Object.keys(jobs).length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <p>📭 Нет активных задач</p>
                    <small>Запустите планировщик для активации автоматических задач</small>
                </div>
            `;
            return;
        }

        let html = '<div class="row">';

        for (const [jobId, job] of Object.entries(jobs)) {
            const nextRun = new Date(job.next_run).toLocaleString('ru-RU');
            const lastRun = job.last_run !== 'Никогда' ? new Date(job.last_run).toLocaleString('ru-RU') : 'Никогда';

            // Иконки для разных типов задач
            let jobIcon = '⚙️';
            let jobName = jobId;
            if (jobId.includes('search')) {
                jobIcon = '🔍';
                jobName = 'Автопоиск вакансий';
            } else if (jobId.includes('health')) {
                jobIcon = '💚';
                jobName = 'Проверка здоровья';
            } else if (jobId.includes('cleanup')) {
                jobIcon = '🧹';
                jobName = 'Очистка данных';
            }

            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${jobIcon} ${jobName}</h6>
                            <p class="card-text">
                                <small class="text-muted">ID: ${jobId}</small><br>
                                <strong>Следующий запуск:</strong> ${nextRun}<br>
                                <strong>Последний запуск:</strong> ${lastRun}<br>
                                <strong>Интервал:</strong> ${job.interval_minutes} мин<br>
                                <strong>Выполнено раз:</strong> ${job.run_count}
                            </p>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar bg-info" role="progressbar" style="width: ${Math.min((job.run_count * 10), 100)}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    setButtonLoading(buttonId, isLoading) {
        const btn = document.getElementById(buttonId);
        const spinner = document.getElementById(buttonId.replace('Btn', 'Spinner'));

        if (isLoading) {
            btn.disabled = true;
            if (spinner) spinner.style.display = 'inline-block';
        } else {
            btn.disabled = false;
            if (spinner) spinner.style.display = 'none';
        }
    }

    showMessage(message, type) {
        // Создаем toast уведомление
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    showError(message) {
        this.showMessage(message, 'danger');
    }

    startAutoRefresh() {
        // Автоматически обновляем статус каждые 30 секунд
        this.statusCheckInterval = setInterval(() => {
            this.loadStatus();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
    }
}

// Инициализация
let schedulerManager;
document.addEventListener('DOMContentLoaded', function() {
    schedulerManager = new SchedulerManager();
});

// Очистка при уходе со страницы
window.addEventListener('beforeunload', function() {
    if (schedulerManager) {
        schedulerManager.stopAutoRefresh();
    }
});