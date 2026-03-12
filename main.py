from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from langdetect import detect, DetectorFactory, LangDetectException
from datetime import datetime
import numpy as np 
import json
import joblib
import os
import logging
from typing import Optional

# === КОНФИГУРАЦИЯ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = 'ml/query_model.pkl'
LOG_FILE = "queries_log.jsonl"

# Параметры из переменных окружения
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8001,http://127.0.0.1:8001").split(",")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.2"))

# Валидация данных
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)

    class Config:
        example = {"query": "Python fastapi tutorial"}


app = FastAPI(title="Pynex Search API", version="1.0.0")

# Настройка для стабильности определения языка
DetectorFactory.seed = 0

# Настройка доступа (CORS) - БЕЗОПАСНО
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

# --- ЗАГРУЗКА ML-МОДЕЛИ ---

def load_ml_model() -> Optional[object]:
    """Загружает обученную ML-модель из файла"""
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            logger.info(f"✓ Модель загружена успешно. Классы: {model.classes_}")
            return model
        except Exception as e:
            logger.error(f"✗ Ошибка при загрузке модели: {e}")
            return None
    else:
        logger.warning(f"⚠ Файл модели не найден по пути: {MODEL_PATH}")
        logger.warning("Запусти: python train_model.py")
    return None

# Загружаем модель ОДИН РАЗ при старте
ml_model = load_ml_model()
    

def get_category(query: str) -> str:
    """Классифицирует запрос по категориям с использованием ML-модели
    
    Args:
        query: Текст поискового запроса
        
    Returns:
        Категория запроса или "Uncategorized" / "No Model"
    """
    if not ml_model:
        return "No Model"
    
    try:
        # Получаем вероятности для всех категорий
        probabilities = ml_model.predict_proba([query])[0]
        # Находим индекс максимальной вероятности
        max_idx = np.argmax(probabilities)
        max_score = probabilities[max_idx]
        
        category = ml_model.classes_[max_idx]
        
        # Если уверенность слишком низкая — не рискуем
        if max_score < CONFIDENCE_THRESHOLD:
            logger.debug(f"LOW_CONFIDENCE: {query} -> {category} ({round(max_score*100, 1)}%)")
            return "Uncategorized"
            
        logger.debug(f"✓ {query} -> {category} ({round(max_score*100, 1)}%)")
        return category
        
    except Exception as e:
        logger.error(f"Ошибка при классификации запроса '{query}': {e}")
        return "Error"

# --- ЭНДПОИНТЫ ---

@app.post("/log")
async def log_query(request: QueryRequest) -> dict:
    """Логирует поисковый запрос и классифицирует его по категориям
    
    Args:
        request: QueryRequest с полем 'query'
        
    Returns:
        dict с статусом и предсказанной категорией
        
    Raises:
        HTTPException: Если query пуста или ошибка при логировании
    """
    query = request.query.strip()
    
    if not query:
        logger.warning("Получен пустой запрос")
        raise HTTPException(status_code=400, detail="query не может быть пустым")

    # 1. Определение языка
    try:
        lang = detect(query)
    except LangDetectException as e:
        logger.warning(f"Не удалось определить язык для '{query}': {e}")
        lang = "unknown"
    except Exception as e:
        logger.error(f"Неожиданная ошибка при определении языка: {e}")
        lang = "error"
            
    # 2. Классификация по категории
    category = get_category(query)
    
    # 3. Формирование записи лога
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "language": lang,
        "category": category
    }
    
    # 4. Сохранение в JSONL
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            f.flush()
        logger.info(f"✓ Залогирован запрос: '{query}' [{lang}] -> {category}")
    except IOError as e:
        logger.error(f"✗ Ошибка при сохранении лога: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении лога")
        
    return {
        "status": "success",
        "category": category,
        "language": lang,
        "confidence": "high" if category != "Uncategorized" else "low"
    }


@app.get("/health")
async def health_check() -> dict:
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "model_loaded": ml_model is not None,
        "log_file": os.path.exists(LOG_FILE)
    }


# Раздача статических файлов фронтенда
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✓ Статические файлы подключены")
else:
    logger.warning("⚠ Папка 'static' не найдена")


if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск Pynex Search API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)