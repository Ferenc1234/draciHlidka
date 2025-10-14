let currentData = null;
let currentTableConfig = null;

// Try multiple URL patterns to find the correct path
async function findWorkingBaseUrl(tableName = 'mesta') {
    const possibleUrls = [
        'DrD-Jmena/drd_table_',                           // Standard relative (docs root)
        './DrD-Jmena/drd_table_',                         // Explicit relative
        '/DrD-Jmena/drd_table_',                          // Absolute from site root
        '/draciHlidka/DrD-Jmena/drd_table_',             // GitHub Pages with repo name
        '../DrD-Jmena/drd_table_',                        // Parent directory
    ];
    
    console.log('Testing URL patterns...');
    
    for (const url of possibleUrls) {
        try {
            const testUrl = `${url}${tableName}.json`;
            console.log('Testing:', testUrl);
            const response = await fetch(testUrl);
            if (response.ok) {
                console.log('✓ Working URL pattern found:', url);
                return url;
            }
        } catch (error) {
            console.log('✗ Failed:', url);
        }
    }
    
    console.error('No working URL pattern found!');
    return 'DrD-Jmena/drd_table_'; // fallback
}

let baseUrl = 'DrD-Jmena/drd_table_'; // default
let urlTestingDone = false;

// Fallback table configurations for when dynamic loading fails
const fallbackTableConfigs = {
    jmena: {
        displayField: 'jmeno',
        filters: {
            gender: {
                field: 'pohlavi',
                label: 'Rod',
                options: [
                    {value: 'M', label: 'Mužský'},
                    {value: 'F', label: 'Ženský'}
                ]
            },
            race: {
                field: 'race',
                label: 'Rasa',
                options: [
                    {value: 'clovek', label: 'Člověk'},
                    {value: 'elf', label: 'Elf'},
                    {value: 'trpaslik', label: 'Trpaslík'},
                    {value: 'hobit', label: 'Hobit'},
                    {value: 'kuduk', label: 'Kuduk'},
                    {value: 'kroll', label: 'Kroll'},
                    {value: 'barbar', label: 'Barbar'}
                ]
            },
            class: {
                field: 'class',
                label: 'Povolání',
                options: [
                    {value: 'valecnik', label: 'Válečník'},
                    {value: 'hranicar', label: 'Hraničář'},
                    {value: 'alchymista', label: 'Alchymista'},
                    {value: 'kouzelnik', label: 'Kouzelník'},
                    {value: 'zlodej', label: 'Zloděj'}
                ]
            }
        }
    },
    // Default config for most tables
    default: {
        displayField: 'nazev',
        filters: {
            gender: {
                field: 'rod',
                label: 'Rod',
                options: [
                    {value: 'M', label: 'Mužský'},
                    {value: 'F', label: 'Ženský'},
                    {value: 'N', label: 'Střední'}
                ]
            }
        }
    }
};
window.debugDrD = async function() {
    console.log('=== DrD Debug Information ===');
    console.log('Current URL:', window.location.href);
    console.log('Hostname:', window.location.hostname);
    console.log('Pathname:', window.location.pathname);
    console.log('Current baseUrl:', baseUrl);
    
    console.log('\n=== Testing all URL patterns ===');
    const testTable = 'mesta';
    const patterns = [
        'DrD-Jmena/drd_table_',
        './DrD-Jmena/drd_table_',
        '/DrD-Jmena/drd_table_',
        '/draciHlidka/DrD-Jmena/drd_table_',
        '../DrD-Jmena/drd_table_',
    ];
    
    for (const pattern of patterns) {
        const testUrl = `${pattern}${testTable}.json`;
        try {
            const response = await fetch(testUrl);
            console.log(`${response.ok ? '✓' : '✗'} ${testUrl} (${response.status})`);
            if (response.ok) {
                const data = await response.json();
                console.log(`  → Contains ${data.data?.length || 0} entries`);
            }
        } catch (error) {
            console.log(`✗ ${testUrl} (Error: ${error.message})`);
        }
    }
    
    console.log('\n=== End Debug ===');
};

// Loading control functions
function showLoading(text = 'Načítám data...', subtext = 'Prosím čekejte') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const loadingSubtext = document.getElementById('loadingSubtext');
    const generateButton = document.querySelector('.btn');
    
    if (loadingText) loadingText.textContent = text;
    if (loadingSubtext) loadingSubtext.textContent = subtext;
    
    if (overlay) {
        overlay.style.display = 'flex';
    }
    
    // Disable the generate button
    if (generateButton) {
        generateButton.disabled = true;
        generateButton.style.opacity = '0.6';
        generateButton.style.cursor = 'not-allowed';
    }
    
    // Also show the simple loading indicator
    const simpleLoading = document.getElementById('loading');
    if (simpleLoading) {
        simpleLoading.style.display = 'block';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    const simpleLoading = document.getElementById('loading');
    const generateButton = document.querySelector('.btn');
    
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    // Re-enable the generate button
    if (generateButton) {
        generateButton.disabled = false;
        generateButton.style.opacity = '1';
        generateButton.style.cursor = 'pointer';
    }
    
    if (simpleLoading) {
        simpleLoading.style.display = 'none';
    }
}

// Add a minimum loading time for better UX
async function showLoadingWithMinTime(text, subtext, minTime = 500) {
    showLoading(text, subtext);
    await new Promise(resolve => setTimeout(resolve, minTime));
}

async function hideLoadingWithDelay(delay = 100) {
    await new Promise(resolve => setTimeout(resolve, delay));
    hideLoading();
}

function updateFilters() {
    const selectedTable = document.getElementById('tableSelect').value;
    const filtersSection = document.getElementById('filtersSection');
    
    // Hide all filters first
    filtersSection.style.display = 'none';
    
    if (!selectedTable) return;
    
    // Clear current data to force reload
    currentData = null;
    currentTableConfig = null;
    
    // Load table configuration and set up filters
    loadTableConfig(selectedTable);
}

async function loadTableConfig(tableName) {
    try {
        showLoading('Načítám konfiguraci...', 'Připravuji filtry');
        
        // Test URL patterns if not done yet
        if (!urlTestingDone) {
            baseUrl = await findWorkingBaseUrl(tableName);
            urlTestingDone = true;
        }
        
        const url = `${baseUrl}${tableName}.json`;
        console.log('Loading table config from:', url);
        
        const response = await fetch(url);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}, url: ${url}`);
        }
        
        const data = await response.json();
        console.log('Loaded table config:', data.name, 'with', Object.keys(data.filters || {}).length, 'filters');
        currentTableConfig = data;
        
        // Set up filters based on table configuration
        setupDynamicFilters(data.filters || {});
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        console.error('Error loading table config:', error);
        console.error('Attempted URL:', `${baseUrl}${tableName}.json`);
        
        // Try fallback configuration
        console.log('Trying fallback configuration for:', tableName);
        const fallbackConfig = fallbackTableConfigs[tableName] || fallbackTableConfigs.default;
        
        currentTableConfig = {
            name: tableName,
            displayField: fallbackConfig.displayField,
            filters: fallbackConfig.filters,
            data: [] // Will be loaded separately
        };
        
        setupDynamicFilters(fallbackConfig.filters);
        
        showResult([`Varování: Použita záložní konfigurace pro ${tableName}`, 
                   'Některé filtry nemusí fungovat správně'], 'error');
    }
}

function setupDynamicFilters(filters) {
    const filtersSection = document.getElementById('filtersSection');
    const filtersContainer = document.getElementById('dynamicFilters');
    
    // Create dynamic filters container if it doesn't exist
    if (!filtersContainer) {
        const container = document.createElement('div');
        container.id = 'dynamicFilters';
        filtersSection.appendChild(container);
    } else {
        filtersContainer.innerHTML = '';
    }
    
    if (Object.keys(filters).length === 0) {
        filtersSection.style.display = 'none';
        return;
    }
    
    filtersSection.style.display = 'block';
    
    const filterKeys = Object.keys(filters);
    
    // Special handling for tables with both race and class filters
    if (filterKeys.includes('race') && filterKeys.includes('class')) {
        // Create gender filter separately if it exists
        if (filterKeys.includes('gender')) {
            const genderFilter = createFilterElement('gender', filters.gender);
            filtersContainer.appendChild(genderFilter);
        }
        
        // Create a row container for race and class filters
        const rowContainer = document.createElement('div');
        rowContainer.className = 'filter-row-container';
        
        const raceFilter = createFilterElement('race', filters.race);
        const classFilter = createFilterElement('class', filters.class);
        
        rowContainer.appendChild(raceFilter);
        rowContainer.appendChild(classFilter);
        filtersContainer.appendChild(rowContainer);
    } else {
        // Create filters normally for other tables
        Object.entries(filters).forEach(([filterKey, filterConfig]) => {
            const filterDiv = createFilterElement(filterKey, filterConfig);
            filtersContainer.appendChild(filterDiv);
        });
    }
}

function createFilterElement(filterKey, filterConfig) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    
    const label = document.createElement('label');
    label.setAttribute('for', `${filterKey}Select`);
    label.textContent = filterConfig.label;
    
    const select = document.createElement('select');
    select.id = `${filterKey}Select`;
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Jakýkoliv --';
    select.appendChild(defaultOption);
    
    // Add filter options
    filterConfig.options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        select.appendChild(optionElement);
    });
    
    formGroup.appendChild(label);
    formGroup.appendChild(select);
    
    return formGroup;
}

async function loadTableData(tableName) {
    try {
        showLoading('Načítám data...', 'Zpracovávám databázi');
        
        // If we already have the config loaded, use it
        if (!currentTableConfig) {
            console.warn('No table config loaded, trying to load data only');
            
            // Try to load with current baseUrl
            let url = `${baseUrl}${tableName}.json`;
            console.log('Loading table data from:', url);
            
            let response = await fetch(url);
            console.log('Data response status:', response.status);
            
            // If that fails and we haven't tested URLs yet, try other patterns
            if (!response.ok && !urlTestingDone) {
                console.log('Primary URL failed, testing alternatives...');
                baseUrl = await findWorkingBaseUrl(tableName);
                urlTestingDone = true;
                url = `${baseUrl}${tableName}.json`;
                response = await fetch(url);
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, url: ${url}`);
            }
            
            const fullData = await response.json();
            
            // If we got the full structure with metadata, use it
            if (fullData.filters && fullData.displayField) {
                currentTableConfig = fullData;
            } else {
                // Otherwise create a minimal config with the data
                const fallbackConfig = fallbackTableConfigs[tableName] || fallbackTableConfigs.default;
                currentTableConfig = {
                    name: tableName,
                    displayField: fallbackConfig.displayField,
                    filters: fallbackConfig.filters,
                    data: fullData.data || fullData
                };
            }
            
            console.log('Loaded data for table:', tableName, 'with', currentTableConfig.data?.length || 0, 'entries');
        }
        
        hideLoading();
        
        return currentTableConfig.data || [];
    } catch (error) {
        hideLoading();
        console.error('Error loading data:', error);
        console.error('Attempted URL:', `${baseUrl}${tableName}.json`);
        throw error;
    }
}

function applyFilters(data, tableName) {
    if (!currentTableConfig || !currentTableConfig.filters) return data;
    
    let filtered = [...data];
    
    // Apply each filter based on the table configuration
    Object.entries(currentTableConfig.filters).forEach(([filterKey, filterConfig]) => {
        const selectElement = document.getElementById(`${filterKey}Select`);
        if (!selectElement) return;
        
        const filterValue = selectElement.value;
        if (!filterValue) return;
        
        if (filterKey === 'gender') {
            // Gender filter - direct field comparison
            filtered = filtered.filter(item => item[filterConfig.field] === filterValue);
        } else if (filterKey === 'race' || filterKey === 'class') {
            // Race/class filters - check if the field equals '1'
            filtered = filtered.filter(item => item[filterValue] === '1');
        } else {
            // Generic binary or direct field filters
            filtered = filtered.filter(item => {
                const itemValue = item[filterConfig.field];
                return itemValue === filterValue;
            });
        }
    });
    
    return filtered;
}

function formatResult(item, tableName) {
    let resultText = '';
    
    if (currentTableConfig && currentTableConfig.displayField) {
        resultText = item[currentTableConfig.displayField] || 'Neznámá položka';
    } else {
        // Fallback for tables without configuration
        resultText = item.nazev || item.jmeno || item.name || 
                    item.pad1 || Object.values(item)[0] || 'Neznámá položka';
    }
    
    // Add gender indicator for names
    if (tableName === 'jmena' && item.pohlavi) {
        const gender = item.pohlavi === 'M' ? '♂️' : item.pohlavi === 'F' ? '♀️' : '';
        resultText += ` ${gender}`;
    }
    
    return resultText;
}

async function generateRandom() {
    const select = document.getElementById('tableSelect');
    const selectedTable = select.value;
    const countSelect = document.getElementById('countSelect');
    const count = parseInt(countSelect.value) || 1;
    
    if (!selectedTable) {
        showResult(['Prosím vyberte kategorii!'], 'error');
        return;
    }

    try {
        showLoading('Generujem položky...', 'Načítám a filtruji data');
        
        // Load data if not already loaded or if different table
        if (!currentData || currentData.tableName !== selectedTable) {
            showLoading('Načítám databázi...', 'Zpracovávám data');
            currentData = {
                tableName: selectedTable,
                data: await loadTableData(selectedTable)
            };
        }

        showLoading('Aplikuji filtry...', 'Zpracovávám výsledky');
        
        // Apply filters
        const filteredData = applyFilters(currentData.data, selectedTable);
        
        showLoading('Počítám statistiky...', 'Aktualizuji údaje');
        
        // Update stats
        document.getElementById('totalEntries').textContent = 
            currentData.data.length.toLocaleString('cs-CZ');
        document.getElementById('filteredEntries').textContent = 
            filteredData.length.toLocaleString('cs-CZ');
        document.getElementById('stats').style.display = 'flex';

        // Generate random items
        if (filteredData.length === 0) {
            hideLoading();
            showResult(['Žádné položky nevyhovují zadaným filtrům!'], 'error');
            return;
        }

        showLoading('Generuji náhodné výsledky...', 'Vybírám položky');

        const results = [];
        const usedIndices = new Set();
        
        for (let i = 0; i < count && i < filteredData.length; i++) {
            let randomIndex;
            do {
                randomIndex = Math.floor(Math.random() * filteredData.length);
            } while (usedIndices.has(randomIndex) && usedIndices.size < filteredData.length);
            
            usedIndices.add(randomIndex);
            const randomItem = filteredData[randomIndex];
            const resultText = formatResult(randomItem, selectedTable);
            results.push(resultText);
        }
        
        hideLoading();
        showResult(results, 'success');

    } catch (error) {
        hideLoading();
        showResult([`Chyba při načítání dat: ${error.message}`], 'error');
    }
}

function showResult(results, type = 'success') {
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    if (Array.isArray(results)) {
        if (results.length === 1) {
            resultContent.innerHTML = results[0];
        } else {
            resultContent.innerHTML = results.map((result, index) => 
                `<div class="result-item">${index + 1}. ${result}</div>`
            ).join('');
        }
    } else {
        resultContent.innerHTML = results;
    }
    
    resultDiv.className = `result ${type}`;
    resultDiv.style.display = 'block';
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcut
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            generateRandom();
        }
    });
    
    // Prevent clicks on loading overlay
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
    }
});