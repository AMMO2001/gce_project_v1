"""
Расширенная аналитика поисковых логов
Показывает иерархию категорий/языков и динамику интересов
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


def run_smart_analytics() -> Optional[pd.DataFrame]:
    """Выполняет расширенный анализ с Sunburst и временной динамикой
    
    Returns:
        DataFrame с анализированными данными или None если ошибка
    """
    if not os.path.exists(LOG_FILE):
        logger.warning(f"⚠️ Файл логов не найден: {LOG_FILE}")
        logger.info("Сделайте несколько поисков в приложении, чтобы создать логи")
        return None

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

    df = pd.DataFrame(data)
    logger.info(f"📊 Анализируем {len(df)} запросов...\n")
    
    # Проверяем, есть ли новые колонки (для старых записей их может не быть)
    if 'category' not in df.columns:
        logger.warning("⚠️ Колонка 'category' отсутствует, добавляю значение по умолчанию")
        df['category'] = 'Legacy'
    if 'language' not in df.columns:
        logger.warning("⚠️ Колонка 'language' отсутствует, добавляю значение по умолчанию")
        df['language'] = 'unknown'

    # === ГРАФИК 1: Распределение по категориям и языкам (Sunburst) ===
    logger.info("📊 Строю диаграмму Sunburst (категории → языки)...")
    fig_cat = px.sunburst(
        df, 
        path=['category', 'language'], 
        title='Твоя цифровая экосистема: Категории и Языки',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_cat.show()

    # === ГРАФИК 2: Динамика интересов по времени ===
    logger.info("📈 Строю график динамики интересов...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Группируем по дате и категории
    cat_time = df.groupby([df['timestamp'].dt.date, 'category']).size().reset_index(name='count')
    cat_time.rename(columns={0: 'timestamp'}, inplace=True)
    
    fig_line = px.line(
        cat_time, 
        x='timestamp', 
        y='count', 
        color='category',
        title='Динамика твоих интересов',
        markers=True,
        template='plotly_dark',
        line_shape='spline'
    )
    fig_line.show()
    logger.info("✅ Графики готовы!")
    
    return df


def main():
    """Главная функция"""
    logger.info("=== РАСШИРЁННЫЙ АНАЛИЗ ЛОГОВ ===\n")
    run_smart_analytics()


if __name__ == "__main__":
    main()