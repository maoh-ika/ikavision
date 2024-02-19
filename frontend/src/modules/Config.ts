export const config = {
    aws: {
        region: import.meta.env.VITE_AWS_REGION,
        accessKey: import.meta.env.VITE_AWS_ACCESS_KEY,
        secretKey: import.meta.env.VITE_AWS_ACCESS_KEY,
        battleAnalyzerEndpoint: import.meta.env.VITE_AWS_BATTLE_ANALYZER_ENDPOINT,
        loginUrl: import.meta.env.VITE_AWS_SIGNIN_URL,
        apiKey: import.meta.env.VITE_AWS_API_KEY,
    },
    buki: {
        spec_dir: import.meta.env.VITE_BUKI_SPEC_DIR,
    },
    isDev: () => import.meta.env.VITE_ENVIRONMENT === 'dev'
}