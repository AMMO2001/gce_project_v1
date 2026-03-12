// === КОНФИГУРАЦИЯ ФРОНТЕНДА ===
// Поскольку static файлы раздаются с бэкенда, можно использовать относительные URL

const CONFIG = {
  // API конфигурация
  API: {
    BASE_URL: 'http://localhost:8001', // ← ИЗМЕНЕНО: localhost вместо 127.0.0.1
    LOG_ENDPOINT: '/log',
    HEALTH_ENDPOINT: '/health',
    TIMEOUT: 5000, // мс
  },
  
  // Google Custom Search Engine
  GOOGLE: {
    // ⚠️ ВАЖНО: Замените на ваш CX ID
    // Получить можно: https://programmablesearchengine.google.com/cse/create/new
    CX: '7710f95b27df946a1', // ЗАМЕНИТЕ НА ВАШЕ ЗНАЧЕНИЕ
    SCRIPT_SRC: 'https://cse.google.com/cse.js', // Не менять!
  },
  
  // p5.js 3D визуализация
  VISUALIZATION: {
    NUM_PARTICLES: 2400,      // Количество точек (больше = красивее, но медленнее)
    TRANSITION_TIME: 150,     // Скорость смены форм
    CHECK_INPUT_INTERVAL: 50, // ms - частота проверки инпута
  },
  
  // Логирование
  LOGGING: {
    ENABLED: true,
    LEVEL: 'debug', // 'debug', 'info', 'warn', 'error'
  },
  
  // Плагины и интеграция
  PLUGINS: {
    P5_JS_VERSION: '1.4.0', // Версия p5.js из CDN
  }
};

/**
 * Получить полный URL API эндпоинта
 * @param {string} endpoint - путь эндпоинта (e.g. '/log')
 * @returns {string} полный URL
 */
function getApiUrl(endpoint) {
  return CONFIG.API.BASE_URL + CONFIG.API.LOG_ENDPOINT;
}

/**
 * Логирование в консоль (если включено)
 * @param {string} level - уровень ('debug', 'info', 'warn', 'error')
 * @param {*} message - сообщение
 */
function log(level, message) {
  if (!CONFIG.LOGGING.ENABLED) return;
  
  const timestamp = new Date().toLocaleTimeString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
  
  switch (level) {
    case 'debug':
      if (CONFIG.LOGGING.LEVEL === 'debug') console.log(prefix, message);
      break;
    case 'info':
      console.info(prefix, message);
      break;
    case 'warn':
      console.warn(prefix, message);
      break;
    case 'error':
      console.error(prefix, message);
      break;
  }
}
