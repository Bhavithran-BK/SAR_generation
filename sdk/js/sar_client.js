class SARClient {
    constructor(baseUrl = "http://localhost:8000/api/v1", apiKey = null) {
        this.baseUrl = baseUrl;
        this.headers = {
            "Content-Type": "application/json"
        };
        if (apiKey) {
            this.headers["X-API-Key"] = apiKey;
        }
    }

    async generateSAR(data) {
        const response = await fetch(`${this.baseUrl}/generation/generate`, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const detail = errorData.detail ? JSON.stringify(errorData.detail) : response.statusText;
            throw new Error(`Error ${response.status}: ${detail}`);
        }
        return await response.json();
    }

    async getStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/generation/status/${jobId}`, {
            headers: this.headers
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const detail = errorData.detail ? JSON.stringify(errorData.detail) : response.statusText;
            throw new Error(`Status Check Error ${response.status}: ${detail}`);
        }
        return await response.json();
    }
}
