// Simple client-side API simulation for GitHub Pages
class SimpleAPI {
    constructor() {
        this.data = {
            message: 'Hello from JavaScript API!',
            timestamp: new Date().toISOString(),
            endpoints: [
                { path: '/', method: 'GET', description: 'Get welcome message' },
                { path: '/data', method: 'GET', description: 'Get sample data' },
                { path: '/status', method: 'GET', description: 'Get API status' }
            ]
        };
    }

    // Handle GET requests
    handleGet(path) {
        switch(path) {
            case '/':
                return {
                    status: 200,
                    data: {
                        message: this.data.message,
                        timestamp: new Date().toISOString()
                    }
                };
            
            case '/data':
                return {
                    status: 200,
                    data: {
                        items: [
                            { id: 1, name: 'Item 1', value: 'Value 1' },
                            { id: 2, name: 'Item 2', value: 'Value 2' },
                            { id: 3, name: 'Item 3', value: 'Value 3' }
                        ],
                        count: 3
                    }
                };
            
            case '/status':
                return {
                    status: 200,
                    data: {
                        status: 'OK',
                        uptime: Date.now(),
                        endpoints: this.data.endpoints
                    }
                };
            
            default:
                return {
                    status: 404,
                    error: 'Endpoint not found'
                };
        }
    }

    // Main API method
    get(path = '/') {
        try {
            const response = this.handleGet(path);
            console.log(`API GET ${path}:`, response);
            return response;
        } catch (error) {
            console.error('API Error:', error);
            return {
                status: 500,
                error: 'Internal server error'
            };
        }
    }
}

// Create global API instance
const api = new SimpleAPI();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimpleAPI;
}

// Example usage:
console.log('JavaScript API initialized');
console.log('Available endpoints:', api.data.endpoints);

// Test the API
console.log('\nTesting API endpoints:');
console.log('GET /', api.get('/'));
console.log('GET /data', api.get('/data'));
console.log('GET /status', api.get('/status'));