"""
ML модель для классификации поисковых запросов по категориям
Использует TF-IDF + Multinomial Naive Bayes
"""

import pandas as pd
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import logging
from typing import Optional

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATASET_PATH = "../dataset.jsonl"
MODEL_PATH = "query_model.pkl"


def train_model() -> Optional[Pipeline]:
    """Обучает ML-модель для классификации запросов
    
    Returns:
        Pipeline: Обученная модель или None если ошибка
    
    Raises:
        FileNotFoundError: Если dataset.jsonl не найден
    """
    data = []
    
    # Читаем датасет
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Ошибка при парсинге строки {line_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        logger.error(f"✗ Файл {DATASET_PATH} не найден!")
        logger.error("Скачайте датасет или создайте его вручную")
        return None
    
    if not data:
        logger.error("✗ Датасет пуст! Добавьте примеры в dataset.jsonl")
        return None
    
    df = pd.DataFrame(data)
    
    # Валидация
    if 'query' not in df.columns or 'category' not in df.columns:
        logger.error("✗ Датасет должен содержать колонки: 'query' и 'category'")
        return None
    
    logger.info(f"📚 Загружено {len(df)} примеров")
    logger.info(f"📊 Категории: {df['category'].unique().tolist()}")
    
    # Создаем Pipeline: TF-IDF → Naive Bayes
    try:
        model = Pipeline([
            ('tfidfvectorizer', TfidfVectorizer(
                ngram_range=(1, 2),     # Учим слова и двухслова
                lowercase=True,
                max_features=5000,
                min_df=2,               # Слово должно встречаться >=2 раз
                max_df=0.9              # Слово не должно быть в >90% документов
            )),
            ('multinomialnb', MultinomialNB(alpha=0.1))
        ])
        
        logger.info("🏋️ Начинаю обучение модели...")
        model.fit(df['query'], df['category'])
        
        # Сохраняем модель
        try:
            joblib.dump(model, MODEL_PATH)
            logger.info(f"✓ Модель успешно сохранена: {MODEL_PATH}")
            logger.info(f"  Размер файла: {joblib.os.path.getsize(MODEL_PATH) / 1024:.1f} KB")
        except Exception as e:
            logger.error(f"✗ Ошибка при сохранении модели: {e}")
            return None
            
        return model
        
    except Exception as e:
        logger.error(f"✗ Ошибка при обучении модели: {e}")
        return None


if __name__ == "__main__":
    logger.info("=== ТРЕНИРОВКА МОДЕЛИ ===")
    model = train_model()
    
    if model:
        logger.info("\n✅ Модель готова к использованию!")
        logger.info("Запустите: uvicorn main:app --reload")
    else:
        logger.error("\n❌ Ошибка при обучении!")