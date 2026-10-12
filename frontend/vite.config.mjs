import {defineConfig, loadEnv} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({mode}) => {
    const env = loadEnv(mode, process.cwd(), 'REACT_APP_')

    return {
        plugins: [react()],
        // Keeps the Create React App conventions the code and the Docker setup rely on
        define: {
            'process.env.REACT_APP_API_URL': JSON.stringify(env.REACT_APP_API_URL || ''),
        },
        server: {
            port: 3000,
            // Keeps the API on the app's origin, as nginx does in production, so the login cookies are sent
            proxy: {
                '/a/': 'http://127.0.0.1:8000',
                '/b/': 'http://127.0.0.1:8000',
                '/media/': 'http://127.0.0.1:8000',
            },
        },
        build: {outDir: 'build'},
    }
})
