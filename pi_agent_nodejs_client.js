// Node.js Integration Example
// npm install axios

const axios = require('axios');

class PiAgentYouTubeClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.client = axios.create({ baseURL });
    }

    async checkStatus(userId = 'default') {
        try {
            const response = await this.client.get('/status', {
                params: { user_id: userId }
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async uploadVideo(userId, filePath, title, description = '', tags = [], privacy = 'private') {
        try {
            const response = await this.client.post('/upload', {
                user_id: userId,
                file_path: filePath,
                title,
                description,
                tags,
                privacy
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async editVideo(userId, videoId, title = null, description = null, privacy = null) {
        try {
            const response = await this.client.post('/edit', {
                user_id: userId,
                video_id: videoId,
                title,
                description,
                privacy
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async executeCommand(userId, command) {
        try {
            const response = await this.client.post('/execute', {
                user_id: userId,
                command
            });
            return response.data;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

// Usage Example
async function main() {
    const client = new PiAgentYouTubeClient();

    try {
        // Check status
        const status = await client.checkStatus('my_user');
        console.log('Status:', status);

        // Upload video
        const uploadResult = await client.uploadVideo(
            'my_user',
            '/path/to/video.mp4',
            'My Video Title',
            'Video description',
            ['tutorial', 'javascript'],
            'private'
        );
        console.log('Upload result:', uploadResult);

        // Edit video
        const editResult = await client.editVideo(
            'my_user',
            'VIDEO_ID_HERE',
            'New Title',
            'New description',
            'public'
        );
        console.log('Edit result:', editResult);

        // Natural language command
        const commandResult = await client.executeCommand(
            'my_user',
            'upload video from /path/video.mp4 titled "My Video"'
        );
        console.log('Command result:', commandResult);

    } catch (error) {
        console.error('Error:', error);
    }
}

module.exports = PiAgentYouTubeClient;

// Uncomment to run directly:
// main();