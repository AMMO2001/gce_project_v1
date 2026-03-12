import joblib

def inspect_brain():
    try:
        model = joblib.load('query_model.pkl')
        vectorizer = model.named_steps['tfidfvectorizer']
        classifier = model.named_steps['multinomialnb']
        
        words = vectorizer.get_feature_names_out()
        categories = classifier.classes_
        
        print("\n АНАЛИЗ ВЕСОВ МОДЕЛИ:")
        print("="*30)

        for i, cat in enumerate(categories):
            # Получаем веса для категории
            weights = classifier.feature_log_prob_[i]
            # Берем индексы 10 самых "тяжелых" слов
            top_indices = weights.argsort()[-10:][::-1]
            
            print(f"\n Категория: {cat.upper()}")
            for idx in top_indices:
                # Вес в логарифмах, поэтому чем ближе к 0, тем важнее слово
                print(f"  - {words[idx]} (вес: {round(weights[idx], 2)})")
                
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    inspect_brain()