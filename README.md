## Быстрый старт: Установка и Запуск
#### 1. Скачивание и распаковка

1. Скачайте архив с проектом.
2. Распакуйте его в любую удобную папку (например, на C:\Projects\).
3. Откройте данную папку в терминале.
4. Создайте и активируйте **виртуальное окружение** (рекомендуется)
``` bash
# Создать окружение
python -m venv venv

# Активировать его (для Windows)
venv\Scripts\activate
```
5. Установите зависимости.
``` bash
pip install -r requirements.txt
```
6. ОБЯЗАТЕЛЬНО! Установите Graphviz, без него деревья рисоваться **НЕ БУДУТ**!
``` bash
choco install graphviz
```
7. Наконец, запустите файл
``` bash
python main.py
```

#### 2. Где лежат сохраненные изображения?
Все результаты (файлы .png) сохраняются в папку results/.

При каждом новом запуске main.py внутри results/ создается уникальная подпапка (например, output_1, output_2 и т.д.).

Пример структуры папок:
```
info_theory_solver/
├── results/
│   ├── output_1/
│   │   ├── Хаффман_Tree_Classic.png
│   │   └── Хаффман_Tree_Scheme.png
│   └── output_2/
│       ├── Хаффман_Tree_Classic.png
│       ├── Хаффман_Tree_Scheme.png
│       └── Шеннон-Фано_Tree_Classic.png
├── algorithms.py
├── main.py
├── metrics.py
├── requirements.txt
└── ...
```
