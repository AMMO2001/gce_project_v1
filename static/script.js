// --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ ---
let particles = [];
const NUM_PARTICLES = CONFIG.VISUALIZATION.NUM_PARTICLES;
let state = 0;
let timer = 0;
let transitionTime = CONFIG.VISUALIZATION.TRANSITION_TIME;
let currentHue = 200;
let targetHue = 200;

function setup() {
    createCanvas(windowWidth, windowHeight, WEBGL);
    colorMode(HSB, 320, 150, 110, 100);
    for (let i = 0; i < NUM_PARTICLES; i++) particles.push(new Particle(i));
    setInterval(checkInput, CONFIG.VISUALIZATION.CHECK_INPUT_INTERVAL);
    log('info', 'p5.js визуализация инициализирована');
}

/*___________________________________*/
/*Блок логирования поисковых запросов*/
/*___________________________________*/

/**
 * Отправляет запрос на бэкенд для логирования
 * @param {string} query - текст запроса
 */
async function sendQueryToBackend(query) {
    if (!query || query.trim() === "") return;

    const url = CONFIG.API.BASE_URL + CONFIG.API.LOG_ENDPOINT;
    const payload = { query: query };

    try {
        log('info', `Отправка запроса: "${query}" -> ${url}`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.API.TIMEOUT);

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        log('info', `✓ Ответ: категория="${data.category}", язык="${data.language}"`);
        
    } catch (err) {
        if (err.name === 'AbortError') {
            log('warn', `Timeout: запрос на ${url} занял более ${CONFIG.API.TIMEOUT}ms`);
        } else {
            log('error', `Ошибка логирования: ${err.message}`);
        }
    }
}
// тут она закончилась

function checkInput() {
let input = document.querySelector('input.gsc-input');
    let placeholder = document.getElementById('custom-placeholder');

    if (input) {
        // Обработчик нажатия Enter для эффекта подмигивания
        if (!input.dataset.hasListener) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const logo = document.getElementById('main-logo');
                    if (logo) {
                        logo.classList.remove('logo-wink');
                        void logo.offsetWidth; // Сброс анимации для повторного запуска
                        logo.classList.add('logo-wink');
                    }
                    sendQueryToBackend(input.value); // Вот здесь мы вызываем функцию логирования
                }
            });
            input.dataset.hasListener = "true";
        }

        const isFocused = (document.activeElement === input);
        const hasText = input.value.length > 0;

        // Логика появления/исчезновения подсказки
        if (isFocused || hasText) {
            placeholder.style.opacity = "0";
            placeholder.style.transform = "scale(0.95)";
        } else {
            placeholder.style.opacity = "1";
            placeholder.style.transform = "scale(1)";
        }

        // Генерация цвета на основе введенных букв
        if (hasText) {
            let hash = 0;
            for (let i = 0; i < input.value.length; i++) {
                hash = input.value.charCodeAt(i) + ((hash << 5) - hash);
            }
            targetHue = Math.abs(hash % 360); // Переводим текст в число от 0 до 360
        } else {
            targetHue = 200; // Стандартный голубой цвет, если текста нет
        }
        // Передаем цвет в CSS (для ссылок в результатах)
        document.documentElement.style.setProperty('--accent-hue', targetHue);
    }
}

function draw() {
    // Плавный переход цвета частиц (0.05 — скорость изменения цвета)
    currentHue = lerp(currentHue, targetHue, 0.05);

    // --- ФОН ---
    background(0); // Всегда чистый черный цвет (0 - яркость)

    // Настройки вращения камеры
    orbitControl(1, 1, 0.1);
    rotateX(frameCount * 0.002); // Скорость вращения по X
    rotateY(frameCount * 0.003); // Скорость вращения по Y

    // --- ОСВЕЩЕНИЕ ---
    // Свет, зависящий от текущего цвета (Hue, Saturation, Brightness)
    ambientLight(currentHue, 50, 40);
    pointLight(0, 0, 100, 200, -200, 300); // Белый точечный источник для бликов

    // Логика таймера для смены геометрических фигур
    timer++;
    if (timer > transitionTime * 2.5) {
        state = (state + 1) % 4;
        timer = 0;
    }

    // Расчет плавности движения (Easing)
    let t = map(timer, 0, transitionTime, 0, 1, true);
    let ease = t * t * (3 - 2 * t);

    // Отрисовка каждой частицы
    particles.forEach(p => {
        p.update(state, ease);
        p.display(currentHue);
    });
}

class Particle {
    constructor(index) {
        this.index = index;
        this.radius = 160; // Общий размер фигур

        // Математика расположения точек (сферы, спирали и т.д.)
        let phi = acos(1 - 2 * (index / NUM_PARTICLES));
        let theta = sqrt(NUM_PARTICLES * PI) * phi;

        // Позиция 1: Сфера
        this.pos1 = createVector(this.radius * sin(phi) * cos(theta), this.radius * sin(phi) * sin(theta), this.radius * cos(phi));

        // Позиция 2: Разлетающиеся ветви
        let branch = index % 7;
        let r2 = this.radius * 2.5;
        let ang = (TWO_PI / 7) * branch + noise(index) * 5;
        this.posMid = createVector(r2 * cos(ang), r2 * sin(ang), sin(index * 0.2) * 300);

        // Позиция 3: Двойная сфера
        let side = (index % 2 === 0) ? -1 : 1;
        this.posTarget = createVector(this.radius * sin(phi) * cos(theta) + (side * this.radius * 1.5), 
                                      this.radius * sin(phi) * sin(theta), this.radius * cos(phi));

        this.currentPos = this.pos1.copy();
    }

    update(state, ease) {
        let target;
        // Переключение между целями в зависимости от состояния
        if (state === 0) target = this.pos1;
        else if (state === 1) target = p5.Vector.lerp(this.pos1, this.posMid, ease);
        else if (state === 2) target = p5.Vector.lerp(this.posMid, this.posTarget, ease);
        else target = this.posTarget;

        // Пульсация (размер 1 + синусоида)
        let pulse = 1 + sin(frameCount * 0.05 + this.index) * 0.02;
        // 0.1 — вязкость движения (чем меньше, тем "ленивее" летят частицы)
        this.currentPos.lerp(p5.Vector.mult(target, pulse), 0.1);
    }

    display(h) {
        push();
        translate(this.currentPos.x, this.currentPos.y, this.currentPos.z);

        // particleHue: цвет частицы + небольшое смещение для разнообразия
        let particleHue = (h + (state * 30)) % 360;
        fill(particleHue, 70, 90); // (Цвет, Насыщенность, Яркость)
        noStroke();

        // sphere(размер, детализация_X, детализация_Y)
        // Маленькие значения (4, 4) делают частицы кубическими/гранеными — это быстрее для браузера
        sphere(1, 8, 8);
        pop();
    }
}

function windowResized() { resizeCanvas(windowWidth, windowHeight); }

