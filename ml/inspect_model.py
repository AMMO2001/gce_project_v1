"""
Инспекция обученной ML-модели
Показывает ключевые слова для каждой категории
"""

import joblib
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = 'query_model.pkl'


def inspect_brain() -> None:
    """Анализирует веса обученной модели и выводит ключевые слова"""
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = model.named_steps['tfidfvectorizer']
        classifier = model.named_steps['multinomialnb']
        
        words = vectorizer.get_feature_names_out()
        categories = classifier.classes_
        
        logger.info("\n" + "="*50)
        logger.info("📊 АНАЛИЗ ВЕСОВ МОДЕЛИ")
        logger.info("="*50)

        for i, cat in enumerate(categories):
            # Получаем веса для категории
            weights = classifier.feature_log_prob_[i]
            # Берем индексы 10 самых "важных" слов для категории
            top_indices = weights.argsort()[-10:][::-1]
            
            logger.info(f"\n🏷️ Категория: {cat.upper()}")
            logger.info("-" * 40)
            
            for rank, idx in enumerate(top_indices, 1):
                word = words[idx]
                weight = round(weights[idx], 3)
                logger.info(f"  {rank:2d}. {word:20s} (вес: {weight})")
                
        logger.info("\n" + "="*50)
        logger.info("✅ Анализ завершен")
        
    except FileNotFoundError:
        logger.error(f"✗ Модель не найдена: {MODEL_PATH}")
        logger.error("Запустите: python train_model.py")
    except Exception as e:
        logger.error(f"✗ Ошибка при анализе: {e}")


if __name__ == "__main__":
    inspect_brain()