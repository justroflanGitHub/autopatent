// Modern Patent Search Application

class PatentSearchApp {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentPatents = [];
        this.currentTrendsData = null;
        this.init();
    }

    init() {
        this.setupDatePickers();
        this.setupEventListeners();
        this.setupModal();
    }

    setupDatePickers() {
        // Initialize Flatpickr date pickers with Russian locale
        const dateConfig = {
            locale: "ru",
            dateFormat: "Y-m-d",
            allowInput: true,
            clickOpens: true,
            wrap: true
        };

        flatpickr("#dateFrom", {
            ...dateConfig,
            placeholder: "YYYY-MM-DD"
        });

        flatpickr("#dateTo", {
            ...dateConfig,
            placeholder: "YYYY-MM-DD"
        });
    }

    setupEventListeners() {
        // Search form submission
        const searchForm = document.getElementById('searchForm');
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // Clustering button
        const clusterBtn = document.getElementById('clusterBtn');
        clusterBtn.addEventListener('click', () => {
            this.performClustering();
        });

        // Trends button
        const trendsBtn = document.getElementById('trendsBtn');
        trendsBtn.addEventListener('click', () => {
            this.showTrends();
        });

        // Close chart button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'closeChartBtn') {
                this.closeChart();
            }
        });

        // Patent card clicks
        document.addEventListener('click', (e) => {
            const patentCard = e.target.closest('.patent-card');
            if (patentCard) {
                const patentId = patentCard.getAttribute('data-patent-id');
                if (patentId) {
                    this.showPatentDetails(patentId);
                }
            }
        });
    }

    // Modal functionality removed - now using separate page

    async performSearch() {
        const formData = this.getFormData();
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBase}/api/search?${this.buildQueryString(formData)}`);
            const data = await response.json();

            if (response.ok) {
                this.currentPatents = data.patents;
                this.displayResults(data);
            } else {
                this.showError('Ошибка при выполнении поиска');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Произошла ошибка при подключении к серверу');
        } finally {
            this.hideLoading();
        }
    }

    async performClustering() {
        if (this.currentPatents.length === 0) {
            this.showError('Сначала выполните поиск патентов');
            return;
        }

        const query = document.getElementById('query').value;
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBase}/api/cluster?query=${encodeURIComponent(query)}&limit=20`, {
                method: 'POST'
            });
            const data = await response.json();

            if (response.ok) {
                this.displayClusters(data);
            } else {
                this.showError('Ошибка при кластеризации');
            }
        } catch (error) {
            console.error('Clustering error:', error);
            this.showError('Произошла ошибка при кластеризации');
        } finally {
            this.hideLoading();
        }
    }

    async showTrends() {
        const query = document.getElementById('query').value || '';
        const trendYears = document.getElementById('trendYears').value || '5';
        // Try to get from results section first, then from form
        const trendsLimitElement = document.getElementById('trendsLimit') || document.getElementById('trendLimit');
        const trendLimit = trendsLimitElement ? trendsLimitElement.value : '100';
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBase}/api/trends?query=${encodeURIComponent(query)}&period_years=${trendYears}&limit=${trendLimit}`);
            const data = await response.json();

            if (response.ok) {
                this.displayTrendsSimple(data);
            } else {
                this.showError('Ошибка при получении трендов');
            }
        } catch (error) {
            console.error('Trends error:', error);
            this.showError('Произошла ошибка при получении трендов');
        } finally {
            this.hideLoading();
        }
    }

    async showIPCTrends(ipcCode) {
        const query = document.getElementById('query').value || '';
        const trendsLimitElement = document.getElementById('trendsLimit') || document.getElementById('trendLimit');
        const limit = trendsLimitElement ? trendsLimitElement.value : '100';
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBase}/api/ipc-trends/${encodeURIComponent(ipcCode)}?query=${encodeURIComponent(query)}&limit=${limit}`);
            const data = await response.json();

            if (response.ok) {
                this.displayIPCTrends(data, ipcCode);
            } else {
                this.showError('Ошибка при получении трендов IPC');
            }
        } catch (error) {
            console.error('IPC Trends error:', error);
            this.showError('Произошла ошибка при получении трендов IPC');
        } finally {
            this.hideLoading();
        }
    }

    async showIPCChart(ipcCode) {
        const query = document.getElementById('query').value || '';
        const trendsLimitElement = document.getElementById('trendsLimit') || document.getElementById('trendLimit');
        const limit = trendsLimitElement ? trendsLimitElement.value : '100';
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBase}/api/ipc-trends/${encodeURIComponent(ipcCode)}?query=${encodeURIComponent(query)}&limit=${limit}`);
            const data = await response.json();

            if (response.ok) {
                this.displayIPCChart(data, ipcCode);
            } else {
                this.showError('Ошибка при получении данных для графика');
            }
        } catch (error) {
            console.error('IPC Chart error:', error);
            this.showError('Произошла ошибка при получении данных для графика');
        } finally {
            this.hideLoading();
        }
    }

    showPatentDetails(patentId) {
        // Redirect to the dedicated patent details page
        window.location.href = `/static/patent.html?id=${encodeURIComponent(patentId)}`;
    }

    getFormData() {
        const form = document.getElementById('searchForm');
        const formData = new FormData(form);

        return {
            query: formData.get('query'),
            limit: formData.get('limit'),
            author: formData.get('author'),
            countries: formData.get('countries'),
            ipc_codes: formData.get('ipc_codes'),
            date_from: formData.get('date_from'),
            date_to: formData.get('date_to')
        };
    }

    buildQueryString(data) {
        const params = new URLSearchParams();

        Object.entries(data).forEach(([key, value]) => {
            if (value && value.trim()) {
                params.append(key, value.trim());
            }
        });

        return params.toString();
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContainer = document.getElementById('resultsContainer');

        if (data.patents.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center" style="padding: 3rem; color: var(--text-secondary);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>По вашему запросу ничего не найдено</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">Попробуйте изменить параметры поиска</p>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = data.patents.map(patent => this.createPatentCard(patent)).join('');
        }

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createPatentCard(patent) {
        const authors = patent.authors.slice(0, 2).join(', ') + (patent.authors.length > 2 ? ' и др.' : '');
        const ipcTags = patent.ipc_codes.slice(0, 3).map(code => `<span class="patent-tag">${code}</span>`).join('');

        // Определяем отображение названия
        let displayText = patent.id;
        if (patent.title && patent.title !== patent.id && !patent.title.startsWith('Патент ')) {
            displayText = `${patent.id} - ${patent.title}`;
        }

        return `
            <div class="patent-card" data-patent-id="${this.escapeHtml(patent.id)}">
                <div class="patent-title">${this.escapeHtml(displayText)}</div>
                <div class="patent-meta">
                    ${authors ? `<div class="patent-authors"><i class="fas fa-user"></i> ${this.escapeHtml(authors)}</div>` : ''}
                    ${patent.publication_date ? `<div class="patent-date"><i class="fas fa-calendar"></i> ${patent.publication_date}</div>` : ''}
                </div>
                <div class="patent-abstract">${this.escapeHtml(patent.abstract)}</div>
                ${ipcTags ? `<div class="patent-tags">${ipcTags}</div>` : ''}
            </div>
        `;
    }

    displayClusters(data) {
        const resultsContainer = document.getElementById('resultsContainer');

        if (!data.clusters || data.clusters.length === 0) {
            resultsContainer.innerHTML = '<p>Не удалось выполнить кластеризацию</p>';
            return;
        }

        const clustersHtml = data.clusters.map(cluster => `
            <div class="cluster-card" style="margin-bottom: 2rem; padding: 1.5rem; border: 1px solid var(--border-color); border-radius: var(--border-radius);">
                <h3 style="color: var(--primary-color); margin-bottom: 1rem;">
                    <i class="fas fa-sitemap"></i> ${this.escapeHtml(cluster.theme)}
                </h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                    ${cluster.count} патентов в кластере
                </p>
                <div style="display: grid; gap: 0.5rem;">
                    ${cluster.patents.slice(0, 5).map(patent => `
                        <div class="patent-card" style="padding: 0.5rem; background: var(--background-color); border-radius: 4px; cursor: pointer;" data-patent-id="${this.escapeHtml(patent.id)}">
                            <div style="font-weight: 500; color: var(--primary-color);">${this.escapeHtml(patent.title)}</div>
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">${this.escapeHtml(patent.authors.join(', '))}</div>
                        </div>
                    `).join('')}
                    ${cluster.patents.length > 5 ? `<div style="text-align: center; color: var(--text-secondary);">... и ещё ${cluster.patents.length - 5} патентов</div>` : ''}
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = clustersHtml;
    }

    displayTrends(data, requestedLimit) {
        const resultsContainer = document.getElementById('resultsContainer');

        if (data.error) {
            resultsContainer.innerHTML = `<p style="color: var(--error-color);">${data.error}</p>`;
            return;
        }

        const trendsHtml = `
            <div style="background: var(--card-background); padding: 2rem; border-radius: var(--border-radius);">
                <h3 style="color: var(--primary-color); margin-bottom: 1.5rem;">
                    <i class="fas fa-chart-line"></i> Анализ трендов патентования
                </h3>

                <div style="background: var(--background-color); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1.5rem; border-left: 4px solid var(--primary-color);">
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                        <i class="fas fa-info-circle"></i>
                        <strong>Параметры анализа:</strong> ${requestedLimit} патентов за период ${data.period.start_year} - ${data.period.end_year}
                        ${data.analyzed_patents !== parseInt(requestedLimit) ? `(проанализировано: ${data.analyzed_patents})` : ''}
                    </p>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="detail-item">
                        <div class="detail-label">Период анализа</div>
                        <div class="detail-value">${data.period.start_year} - ${data.period.end_year}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Общий тренд</div>
                        <div class="detail-value">${data.growth_rates.total ? data.growth_rates.total + '%' : 'Недостаточно данных'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Всего патентов</div>
                        <div class="detail-value">${data.total_patents}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Проанализировано</div>
                        <div class="detail-value">${data.analyzed_patents}</div>
                    </div>
                </div>

                ${data.top_authors.length > 0 ? `
                    <div style="margin-bottom: 2rem;">
                        <h4 style="color: var(--text-primary); margin-bottom: 1rem;">
                            <i class="fas fa-user"></i> Топ-авторы
                        </h4>
                        <div style="display: grid; gap: 0.5rem;">
                            ${data.top_authors.slice(0, 5).map(author => `
                                <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--background-color); border-radius: 4px;">
                                    <span>${this.escapeHtml(author.author)}</span>
                                    <span style="font-weight: 500;">${author.total_patents} патентов</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${data.top_ipc_codes.length > 0 ? `
                    <div>
                        <h4 style="color: var(--text-primary); margin-bottom: 1rem;">
                            <i class="fas fa-tags"></i> Популярные темы
                        </h4>
                        <div style="display: grid; gap: 0.5rem;">
                            ${data.top_ipc_codes
                                .sort((a, b) => b.total_patents - a.total_patents)
                                .slice(0, 5)
                                .map(ipc => {
                                const description = this.getIPCDescription(ipc.ipc_code);
                                const displayText = description ? description : ipc.ipc_code;
                                return `
                                    <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--background-color); border-radius: 4px;">
                                        <span style="color: var(--primary-color); cursor: pointer; transition: all 0.2s; text-decoration: underline;" onclick="window.app.showIPCChart('${ipc.ipc_code.replace(/'/g, "\\'")}')" onmouseover="this.style.color='var(--primary-hover)'; this.style.textDecoration='underline';" onmouseout="this.style.color='var(--primary-color)'; this.style.textDecoration='underline';" title="Кликните для просмотра графика">${this.escapeHtml(displayText)}</span>
                                        <span style="font-weight: 500; color: var(--text-secondary);">${ipc.total_patents} патентов</span>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        resultsContainer.innerHTML = trendsHtml;

        // Добавляем обработчик события для кнопки графика
        const showChartBtn = document.getElementById('showChartBtn');
        if (showChartBtn) {
            showChartBtn.addEventListener('click', () => {
                this.showTrendChart();
            });
        }
    }

    displayTrendsSimple(data) {
        const resultsContainer = document.getElementById('resultsContainer');

        if (data.error) {
            resultsContainer.innerHTML = `<p style="color: var(--error-color);">${data.error}</p>`;
            return;
        }

        // Сохраняем данные для использования в графике
        this.currentTrendsData = data;

        // Создаем простой вывод трендов по годам
        let trendsList = '';
        if (data.yearly_statistics) {
            const sortedYears = Object.keys(data.yearly_statistics).sort();
            trendsList = sortedYears.map(year => {
                const count = data.yearly_statistics[year];
                return `<div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--background-color); border-radius: 4px; margin-bottom: 0.5rem;">
                    <span>Год ${year}</span>
                    <span style="font-weight: 500;">${count} патентов</span>
                </div>`;
            }).join('');
        }

        const trendsHtml = `
            <div style="background: var(--card-background); padding: 2rem; border-radius: var(--border-radius);">
                <h3 style="color: var(--primary-color); margin-bottom: 1.5rem;">
                    <i class="fas fa-chart-line"></i> Анализ трендов патентования
                </h3>

                <div style="background: var(--background-color); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1.5rem; border-left: 4px solid var(--primary-color);">
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                        <i class="fas fa-info-circle"></i>
                        <strong>Параметры анализа:</strong> ${data.total_patents} патентов за период ${data.period.start_year} - ${data.period.end_year}
                    </p>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 1rem;">
                        <i class="fas fa-calendar"></i> Количество патентов по годам
                    </h4>
                    ${trendsList || '<p>Нет данных для отображения</p>'}
                </div>

                ${data.top_ipc_codes && data.top_ipc_codes.length > 0 ? `
                    <div style="margin-bottom: 2rem;">
                        <h4 style="color: var(--text-primary); margin-bottom: 1rem;">
                            <i class="fas fa-tags"></i> Популярные темы
                        </h4>
                        <div style="display: grid; gap: 0.5rem;">
                            ${data.top_ipc_codes.slice(0, 5).map(ipc => {
                                const description = this.getIPCDescription(ipc.ipc_code);
                                const displayText = description ? description : ipc.ipc_code;
                                return `
                                    <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--background-color); border-radius: 4px;">
                                        <span>${this.escapeHtml(displayText)}</span>
                                        <span style="font-weight: 500;">${ipc.total_patents} патентов</span>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}

                <div style="text-align: center; margin-top: 2rem;">
                    <button id="showChartBtn" style="background: var(--primary-color); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: var(--border-radius); cursor: pointer; font-size: 1rem;">
                        <i class="fas fa-chart-bar"></i> Построить график
                    </button>
                </div>
            </div>
        `;

        resultsContainer.innerHTML = trendsHtml;

        // Добавляем обработчик события для кнопки графика
        const showChartBtn = document.getElementById('showChartBtn');
        if (showChartBtn) {
            showChartBtn.addEventListener('click', () => {
                this.showTrendChart();
            });
        }
    }

    showTrendChart() {
        const chartContainer = document.getElementById('chartContainer');
        const chartCanvas = document.getElementById('trendsChart');

        const data = this.currentTrendsData;
        if (!data) {
            this.showError('Нет данных для построения графика');
            return;
        }

        if (data.error) {
            this.showError('Ошибка при получении данных для графика');
            return;
        }

        // Подготавливаем данные для графика
        const years = Object.keys(data.yearly_statistics || {}).sort();
        const patentCounts = years.map(year => data.yearly_statistics[year]);

        // Создаем график
        const ctx = chartCanvas.getContext('2d');

        // Уничтожаем предыдущий график если он существует
        if (window.currentChart) {
            window.currentChart.destroy();
        }

        window.currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: 'Количество патентов по годам',
                    data: patentCounts,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2563eb',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: 10
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Год'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Количество патентов'
                        },
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Тренды патентования по годам',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 30
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        callbacks: {
                            title: function(context) {
                                return `Год: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `Патентов: ${context.raw}`;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        // Устанавливаем фиксированную высоту контейнера графика
        chartContainer.style.height = '500px';
        chartContainer.style.maxHeight = '500px';
        chartContainer.style.overflow = 'hidden';

        // Показываем контейнер с графиком
        chartContainer.style.display = 'block';

        // Прокручиваем к графику плавно, но не резко
        setTimeout(() => {
            const rect = chartContainer.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            const chartTop = rect.top + window.pageYOffset;

            // Прокручиваем так, чтобы график был виден в верхней части экрана
            window.scrollTo({
                top: chartTop - 100, // Отступ от верха экрана
                behavior: 'smooth'
            });
        }, 100);
    }

    displayIPCTrends(data, ipcCode) {
        const resultsContainer = document.getElementById('resultsContainer');

        if (data.error) {
            resultsContainer.innerHTML = `<p style="color: var(--error-color);">${data.error}</p>`;
            return;
        }

        // Получаем описание IPC кода
        const ipcDescription = this.getIPCDescription(ipcCode);

        const ipcTrendsHtml = `
            <div style="background: var(--card-background); padding: 2rem; border-radius: var(--border-radius);">
                <h3 style="color: var(--primary-color); margin-bottom: 1.5rem;">
                    <i class="fas fa-tags"></i> Статистика по теме: ${this.escapeHtml(ipcCode)}
                </h3>

                ${ipcDescription ? `
                    <div style="background: var(--background-color); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1.5rem; border-left: 4px solid var(--primary-color);">
                        <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                            <i class="fas fa-info-circle"></i>
                            <strong>Описание темы:</strong> ${this.escapeHtml(ipcDescription)}
                        </p>
                    </div>
                ` : ''}

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="detail-item">
                        <div class="detail-label">Всего патентов</div>
                        <div class="detail-value">${data.total_patents}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Период</div>
                        <div class="detail-value">${data.period.start_year} - ${data.period.end_year}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Среднее в год</div>
                        <div class="detail-value">${data.avg_per_year}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Рост тренда</div>
                        <div class="detail-value">${data.growth_rate ? data.growth_rate + '%' : 'Недостаточно данных'}</div>
                    </div>
                </div>

                <div style="text-align: center;">
                    <button onclick="window.app.showTrends()" style="background: var(--primary-color); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: var(--border-radius); cursor: pointer; font-size: 1rem;">
                        <i class="fas fa-arrow-left"></i> Назад к трендам
                    </button>
                </div>
            </div>
        `;

        resultsContainer.innerHTML = ipcTrendsHtml;
    }

    displayIPCChart(data, ipcCode) {
        const chartContainer = document.getElementById('chartContainer');
        const chartCanvas = document.getElementById('trendsChart');

        if (data.error) {
            this.showError('Ошибка при получении данных для графика');
            return;
        }

        // Получаем описание IPC кода
        const ipcDescription = this.getIPCDescription(ipcCode);

        // Подготавливаем данные для графика
        const years = Object.keys(data.yearly_data).sort();
        const patentCounts = years.map(year => data.yearly_data[year]);

        // Создаем график
        const ctx = chartCanvas.getContext('2d');

        // Уничтожаем предыдущий график если он существует
        if (window.currentChart) {
            window.currentChart.destroy();
        }

        window.currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: `Количество патентов по теме ${ipcCode}`,
                    data: patentCounts,
                    borderColor: 'var(--primary-color)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'var(--primary-color)',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: ipcDescription ? `${ipcDescription} (${ipcCode})` : `Тема: ${ipcCode}`,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 30
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        callbacks: {
                            title: function(context) {
                                return `Год: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `Патентов: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Год'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Количество патентов'
                        },
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        // Показываем контейнер с графиком
        chartContainer.style.display = 'block';
        chartContainer.scrollIntoView({ behavior: 'smooth' });
    }

    closeChart() {
        const chartContainer = document.getElementById('chartContainer');

        // Уничтожаем график
        if (window.currentChart) {
            window.currentChart.destroy();
            window.currentChart = null;
        }

        // Скрываем контейнер
        chartContainer.style.display = 'none';
    }

    getIPCDescription(ipcCode) {
        // Словарь описаний IPC кодов
        const ipcDescriptions = {
            // G06F - Электрические цифровые машины для обработки данных
            'G06F': 'Электрические цифровые машины для обработки данных',
            'G06F1': 'Электрические цифровые машины для обработки данных вообще',
            'G06F3': 'Ввод данных для обработки',
            'G06F5': 'Методы оптического считывания данных',
            'G06F7': 'Методы или приспособления для обработки данных',
            'G06F9': 'Распределение обработки между несколькими вычислительными элементами',
            'G06F9/30': 'Распределение обработки между несколькими вычислительными элементами',
            'G06F11': 'Обработка ошибок',
            'G06F13': 'Взаимодействие между локальными и удаленными сетевыми станциями',
            'G06F15': 'Цифровые компьютеры вообще; оборудование для обработки данных вообще',
            'G06F15/16': 'Комбинации двух или более цифровых компьютеров',
            'G06F17': 'Цифровые вычислительные машины или аналогичные устройства',
            'G06F17/16': 'Цифровые вычислительные машины или аналогичные устройства',
            'G06F19': 'Цифровые вычислительные машины с изменяемой архитектурой',
            'G06F21': 'Обработка ошибок в вычислительных машинах',

            // G06 - Вычислительная техника, информатика
            'G06': 'Вычислительная техника, информатика',
            'G06B': 'Считывающие устройства',
            'G06C': 'Цифровые компьютеры',
            'G06D': 'Аналоговые компьютеры',
            'G06E': 'Аналоговые вычислительные машины',
            'G06E1': 'Аналоговые вычислительные машины',
            'G06E3': 'Устройства для аналоговых вычислений',
            'G06G': 'Аналоговые или гибридные вычислительные устройства',
            'G06J': 'Гибридные вычислительные устройства',
            'G06K': 'Распознавание образов, обработка изображений',
            'G06M': 'Счетные машины',
            'G06N': 'Информатика, вычислительная техника',
            'G06N20': 'Машинное обучение',
            'G06N20/10': 'Машинное обучение',
            'G06Q': 'Обработка данных для административных целей',
            'G06T': 'Обработка изображений',

            // H04 - Электросвязь
            'H04': 'Электросвязь',
            'H04B': 'Передача информации',
            'H04L': 'Передача информации',
            'H04M': 'Телефонная связь',
            'H04N': 'Передача изображений',
            'H04Q': 'Выбор',
            'H04W': 'Беспроводная связь',

            // G07 - Контрольные механизмы
            'G07': 'Контрольные механизмы',
            'G07D': 'Обработка монет или банкнот',
            'G07D11': 'Устройства для обработки банкнот',
            'G07D11/60': 'Устройства для обработки банкнот',

            // B03 - Разделение смесей
            'B03': 'Разделение смесей',
            'B03C': 'Магнитное или электростатическое разделение',
            'B03C1': 'Магнитное разделение',
            'B03C1/033': 'Магнитное разделение',

            // Другие популярные разделы
            'G05B': 'Системы управления',
            'G01S': 'Радиолокация, радионавигация',
            'H03G': 'Усилители с регулируемым коэффициентом усиления',
            'H01L': 'Полупроводниковые устройства',
            'H02M': 'Преобразование электрической энергии',
            'B60W': 'Совместное регулирование мощности и скорости движения транспортных средств'
        };

        // Ищем точное совпадение
        if (ipcDescriptions[ipcCode]) {
            return ipcDescriptions[ipcCode];
        }

        // Ищем по первым 6 символам (для подклассов типа G06F17/16)
        const prefix6 = ipcCode.substring(0, 6);
        if (ipcDescriptions[prefix6]) {
            return ipcDescriptions[prefix6];
        }

        // Ищем по первым 5 символам
        const prefix5 = ipcCode.substring(0, 5);
        if (ipcDescriptions[prefix5]) {
            return ipcDescriptions[prefix5];
        }

        // Ищем по первым 4 символам
        const prefix4 = ipcCode.substring(0, 4);
        if (ipcDescriptions[prefix4]) {
            return ipcDescriptions[prefix4];
        }

        // Ищем по первым 3 символам
        const prefix3 = ipcCode.substring(0, 3);
        if (ipcDescriptions[prefix3]) {
            return ipcDescriptions[prefix3];
        }

        // Ищем по первым символам раздела
        const section = ipcCode.substring(0, 1);
        const sectionDescriptions = {
            'A': 'Удовлетворение жизненных потребностей человека',
            'B': 'Различные технологические процессы',
            'C': 'Химия, металлургия',
            'D': 'Текстиль, бумага',
            'E': 'Строительство, горное дело',
            'F': 'Машиностроение, освещение, отопление',
            'G': 'Физика',
            'H': 'Электричество'
        };

        if (sectionDescriptions[section]) {
            return `${sectionDescriptions[section]} (${ipcCode})`;
        }

        return null;
    }

    formatPatentAnalysis(analysis) {
        let html = '';

        if (analysis.description) {
            html += `<p><strong>Описание:</strong> ${this.escapeHtml(analysis.description)}</p>`;
        }

        if (analysis.advantages && analysis.advantages.length > 0) {
            html += `<p><strong>Преимущества:</strong></p><ul>`;
            analysis.advantages.forEach(advantage => {
                html += `<li>${this.escapeHtml(advantage)}</li>`;
            });
            html += `</ul>`;
        }

        if (analysis.disadvantages && analysis.disadvantages.length > 0) {
            html += `<p><strong>Недостатки:</strong></p><ul>`;
            analysis.disadvantages.forEach(disadvantage => {
                html += `<li>${this.escapeHtml(disadvantage)}</li>`;
            });
            html += `</ul>`;
        }

        if (analysis.applications && analysis.applications.length > 0) {
            html += `<p><strong>Области применения:</strong></p><ul>`;
            analysis.applications.forEach(application => {
                html += `<li>${this.escapeHtml(application)}</li>`;
            });
            html += `</ul>`;
        }

        return html || '<p>Анализ не доступен</p>';
    }

    formatAnalysis(analysis) {
        let html = '';

        if (analysis.technical_solution) {
            html += `<p><strong>Техническое решение:</strong> ${this.escapeHtml(analysis.technical_solution)}</p>`;
        }

        if (analysis.novelty) {
            html += `<p><strong>Новизна:</strong> ${this.escapeHtml(analysis.novelty)}</p>`;
        }

        if (analysis.application_field) {
            html += `<p><strong>Область применения:</strong> ${this.escapeHtml(analysis.application_field)}</p>`;
        }

        if (analysis.advantages && analysis.advantages.length > 0) {
            html += `<p><strong>Преимущества:</strong></p><ul>`;
            analysis.advantages.forEach(advantage => {
                html += `<li>${this.escapeHtml(advantage)}</li>`;
            });
            html += `</ul>`;
        }

        if (analysis.key_features && analysis.key_features.length > 0) {
            html += `<p><strong>Ключевые особенности:</strong></p><ul>`;
            analysis.key_features.forEach(feature => {
                html += `<li>${this.escapeHtml(feature)}</li>`;
            });
            html += `</ul>`;
        }

        return html || '<p>Анализ не доступен</p>';
    }

    showLoading() {
        const spinner = document.getElementById('loadingSpinner');
        spinner.style.display = 'block';
    }

    hideLoading() {
        const spinner = document.getElementById('loadingSpinner');
        spinner.style.display = 'none';
    }

    showError(message) {
        // Create error toast
        const toast = document.createElement('div');
        toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: var(--error-color); color: white; padding: 1rem 1.5rem; border-radius: var(--border-radius); box-shadow: var(--shadow-lg); z-index: 1001; animation: slideInRight 0.3s ease-out;';
        toast.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span style="margin-left: 0.5rem;">${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 5000);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PatentSearchApp();
});

// Add CSS animations for toasts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
