"""
Базовая аналитика поисковых логов
Показывает активность по часам и топ запросов
"""

import pandas as pd
import plotly.express as px
import json
import os
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

LOG_FILE = "../queries_log.jsonl"


def run_analytics() -> Optional[pd.DataFrame]:
    """Анализирует логи и выводит графики
    
    Returns:
        DataFrame с анализированными данными или None если ошибка
    """
    if not os.path.exists(LOG_FILE):
        logger.warning(f"⚠️ Файл логов не найден: {LOG_FILE}")
        logger.info("Сделайте несколько поисков в приложении, чтобы создать логи")
        return None

    # Читаем JSON (каждая строка — отдельный объект)
    data = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Ошибка в строке {line_num}: {e}")
                    continue
    except IOError as e:
        logger.error(f"✗ Ошибка при чтении файла: {e}")
        return None

    if not data:
        logger.warning("📊 Логи пусты. Сделайте поиски в приложении.")
        return None

    # Создаем DataFrame
    df = pd.DataFrame(data)
    logger.info(f"📊 Анализируем {len(df)} запросов...\n")
    
    # Преобразуем время
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date

    # === ГРАФИК 1: Активность по часам ===
    logger.info("📈 Строю график активности по часам...")
    hourly_counts = df.groupby('hour').size().reset_index(name='counts')
    
    fig = px.bar(hourly_counts, 
                 x='hour', 
                 y='counts',
                 title='Когда ты чаще всего гуглишь? (Активность по часам)',
                 labels={'hour': 'Час суток', 'counts': 'Количество запросов'},
                 template='plotly_dark',
                 color_discrete_sequence=['#00d4ff'])
    fig.show()

    # === ГРАФИК 2: Топ запросов ===
    logger.info("🔝 Строю график топ запросов...")
    top_queries = df['query'].value_counts().head(10).reset_index()
    top_queries.columns = ['query', 'count']
    
    fig2 = px.pie(top_queries, 
                  values='count', 
                  names='query', 
                  title='Топ-10 твоих интересов',
                  template='plotly_dark',
                  hole=0.4)
    
    fig2.show()
    logger.info("✅ График готов!")
    
    return df


def main():
    """Главная функция"""
    logger.info("=== АНАЛИЗ ЛОГОВ ===\n")
    run_analytics()


if __name__ == "__main__":
    main()