# Разработка двухуровневых рекомендательных систем 

Проект состоит из 
- 2step_models: двухуровневые модели
    - XGBoost + LightFM
    - XGBoost + NCF
    - XGBoost + Popular
    - LightAutoML + LightFM + NCF + Popular
- utils: вспомогательные функции
- stat_data: демографичекие данные
- russian_name: файл русских имен
- prediction_1lvl_models: файлы с кандидатами от моделей первого уровня
- models: модель с весами NCF
- data_ncf: предобработанные данные для обучения NCF

Необходимо также установить модуль recommenders: https://github.com/microsoft/recommenders 
За данными обращаться в тг: @maria_farfan
