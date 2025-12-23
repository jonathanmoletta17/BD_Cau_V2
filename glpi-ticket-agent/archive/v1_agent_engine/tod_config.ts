/**
 * Configuration for environment variables
 */

import dotenv from 'dotenv';
dotenv.config();

export const CONFIG = {
    // Feature flag for new TOD architecture
    ENABLE_TOD_ARCHITECTURE: process.env.ENABLE_TOD === 'true',

    // Existing config
    PORT: process.env.PORT || 5000,
    LLM_BASE_URL: process.env.LLM_BASE_URL || 'http://localhost:11434',
    LLM_MODEL: process.env.LLM_MODEL || 'llama3.1:latest',
    REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',

    // GLPI
    GLPI_URL: process.env.GLPI_URL || '',
    GLPI_USER: process.env.GLPI_USER || '',
    GLPI_PASSWORD: process.env.GLPI_PASSWORD || '',
};

console.log('[Config] TOD Architecture:', CONFIG.ENABLE_TOD_ARCHITECTURE ? 'ENABLED' : 'DISABLED');
