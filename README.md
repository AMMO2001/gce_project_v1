# 🔍 Pynex Search Engine

**Умная поисковая система на базе Google Custom Search с ML-классификацией запросов**

## 📋 Описание

Pynex — это современная оболочка над Google Custom Search Engine с интеллектуальной системой логирования и классификации поисковых запросов. Проект использует machine learning для определения языка запроса и его категории, сохраняя все данные в формате JSONL для последующего анализа.

### Ключевые особенности:
- ✨ **Визуальный интерфейс** — красивый 3D-дизайн на базе p5.js
- 🤖 **ML-классификация** — автоматическое определение категории запроса
- 🌍 **Определение языка** — распознание языка поиска (55+ языков)
- 📊 **Аналитика** — интерактивная визуализация логов с Plotly
- 📝 **Логирование** — сохранение всех запросов в JSONL

## 🏗️ Архитектура

```
gce_project_v1/
├── main.py                   # FastAPI бэкенд (логирование, классификация)
├── dataset.jsonl             # Dataset для обучения (query + category)
├── queries_log.jsonl         # Логи реальных поисков (генерируется)
├── requirements.txt          # Зависимости Python
├── .env.example             # Пример переменных окружения
├── .gitignore               # Git конфиг
├── README.md                # Документация
├── static/                  # Фронтенд
│   ├── index.html           # HTML (Google CSE)
│   ├── script.js            # p5.js 3D визуализация + логирование
│   ├── config.js            # Конфигурация API
│   ├── style.css            # Оформление
│   └── images/              # Иконки, фавиконы
├── ml/                      # Машинное обучение 🤖
│   ├── train_model.py       # Обучение ML-модели
│   ├── inspect_model.py     # Анализ весов модели
│   └── query_model.pkl      # Обученная модель (генерируется)
└── analytics/               # Анализ данных 📊
    ├── data_analys.py       # Базовая аналитика логов
    ├── data_analys_two.py   # Расширенная аналитика
    └── analytics.ipynb      # Jupyter ноутбук для анализа
```

## 🚀 Установка и запуск

### 1. Требования
- Python 3.8+
- pip или poetry

### 2. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Конфигурация

Создайте `.env` файл на основе `.env.example`:
```bash
cp .env.example .env
```

Отредактируйте `.env` с вашим Google Custom Search Engine CX ID:
```env
GOOGLE_CSE_CX=ваш_cx_id_здесь
API_URL=http://localhost:8000
```

### 4. Обучение модели (первый раз)
```bash
cd ml
python train_model.py
cd ..
```

Модель обучится на данных из `../dataset.jsonl` и создаст файл `query_model.pkl`.

### 5. Запуск приложения
```bash
uvicorn main:app --reload
```

Откройте в браузере: **http://localhost:8000/static/index.html**

## 📊 Использование

### API Эндпоинт

**POST** `/log` — Логирование нового запроса
```bash
curl -X POST "http://localhost:8000/log" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python fastapi tutorial"}'
```

**Ответ:**
```json
{
  "status": "success",
  "category": "IT"
}
```

### Анализ логов

**Базовый анализ:**
```bash
cd analytics
python data_analys.py
```
Показывает:
- Активность по часам
- Топ-10 запросов

**Расширенная аналитика:**
```bash
python data_analys_two.py
```
Показывает:
- Иерархия категорий и языков (Sunburst)
- Динамика интересов во времени

### Инспекция модели

Посмотреть ключевые слова для каждой категории:
```bash
cd ml
python inspect_model.py
```

## 📁 Описание файлов и папок

| Файл/Папка | Назначение |
|------|-----------|
| **main.py** | FastAPI приложение, эндпоинты `/log` и `/health` |
| **dataset.jsonl** | Обучающий датасет (query, category) |
| **queries_log.jsonl** | Логи реальных поисков (автоматически создается) |
| **ml/** | 🤖 Папка машинного обучения |
| └─ **train_model.py** | Обучение sklearn Pipeline (TF-IDF + Naive Bayes) |
| └─ **inspect_model.py** | Анализ весов и ключевых слов модели |
| └─ **query_model.pkl** | Сохраненная обученная модель |
| **analytics/** | 📊 Папка анализа данных |
| └─ **data_analys.py** | Базовая аналитика (графики по часам, топ запросов) |
| └─ **data_analys_two.py** | Продвинутая аналитика (Sunburst, динамика) |
| └─ **analytics.ipynb** | Jupyter ноутбук для интерактивного анализа |
| **static/** | 🌐 Фронтенд (HTML, CSS, JavaScript) |

## 🔧 ML Модель

**Архитектура:**
- **Векторизация:** TF-IDF с ngrams (1, 2)
- **Классификатор:** Multinomial Naive Bayes (alpha=0.1)
- **Входные данные:** Текст запроса
- **Выходные данные:** Категория + уверенность (%)
- **Порог доверия:** < 20% → "Uncategorized"

**Категории в датасете:**
- IT (программирование, Linux, VS Code)
- Culture (литература, искусство)
- Science (физика, биология)
- Art (живопись, музеи)
- Literature (классика)

## 🔐 Безопасность

⚠️ **Важно перед публикацией:**

1. Не коммитить `.env` файл с настоящими ключами
2. Использовать переменные окружения: `GOOGLE_CSE_CX`
3. В продакшене установить правильные CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["yourdomain.com"],  # Только ваш домен
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

4. Добавить аутентификацию для API
5. Логировать все запросы для аудита

## 📊 Формат данных

### dataset.jsonl
```json
{"query": "Python fastapi tutorial", "category": "IT"}
{"query": "Пушкин стихи", "category": "Culture"}
```

### queries_log.jsonl
```json
{"timestamp": "2026-03-12 14:23:45", "query": "Python fastapi", "language": "en", "category": "IT"}
{"timestamp": "2026-03-12 14:25:10", "query": "Как писать код", "language": "ru", "category": "IT"}
```

## 🛠️ Производительность

- **Время классификации:** ~5ms на запрос
- **Максимум запросов:** ~200 рек/сек
- **Память модели:** ~2MB (query_model.pkl)
- **Размер логов:** ~200 байт на запрос

При росте:
- Рекомендуется добавить Redis кеш
- Перейти на более быстрые модели (CatBoost, LightGBM)
- Сохранять логи в БД вместо JSONL

## 📝 Лицензия

MIT License — используйте свободно! 😊

## 👤 Автор

Создано для демонстрации ML + FastAPI + Google Custom Search Integration

---

**Готов к загрузке на GitHub!** 🚀

Если нашли ошибки — создавайте Issues!
