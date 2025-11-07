import numpy as np

def generate_probabilities(n, prefix='z', min_prob=0.00001, method='uniform', decimals=4):
    """
    Генерирует словарь с вероятностями, сумма которых *точно* равна 1.

    Использует NumPy для высокой производительности и "Метод наибольших остатков"
    (Largest Remainder Method) для гарантии, что сумма округленных
    значений равна 1.0.

    Args:
        n: количество элементов (может быть очень большим, > 1,000,000)
        prefix: префикс для ключей
        min_prob: минимальная допустимая вероятность
        method: метод генерации ('uniform', 'exponential', 'dirichlet', 'loguniform')
        decimals: количество знаков после запятой

    Returns:
        Словарь с вероятностями.
        
    Raises:
        ValueError: Если n <= 0 или min_prob невалиден.
        MemoryError: Если 'n' слишком велико для доступной ОЗУ (например, > 100,000,000).
    """
    
    # --- 1. Валидация входных данных ---
    if n <= 0:
        raise ValueError("Количество элементов 'n' должно быть положительным")
    
    if min_prob <= 0:
         raise ValueError("min_prob должен быть > 0")

    # Проверяем, возможно ли вообще выделить min_prob для n элементов
    # (n * min_prob) должно быть < 1.0
    total_min_prob = n * min_prob
    if total_min_prob >= 1.0:
        raise ValueError(f"min_prob слишком велик для {n} элементов. "
                         f"Максимальный min_prob: {1.0/n:.10f}")

    # --- 2. Генерация весов (NumPy) ---
    # `scale_factor` - это та часть (от 0 до 1), которую мы распределяем *поверх* min_prob
    scale_factor = 1.0 - total_min_prob

    if method == 'dirichlet':
        # Дирихле идеально подходит, так как по определению генерирует
        # n чисел, сумма которых равна 1.
        # Мы просто масштабируем этот "1" до `scale_factor`.
        # alpha > 1 гарантирует отсутствие нулей.
        alpha = np.ones(n) * 1.5
        # `weights` - это массив размером n, сумма которого = 1.0
        weights = np.random.dirichlet(alpha)
        
    else:
        # Для других методов мы генерируем "веса", а затем нормализуем их.
        if method == 'uniform':
            # Генерируем положительные веса
            weights = np.random.uniform(0.1, 1.0, size=n)
        elif method == 'exponential':
            weights = np.random.exponential(scale=1.0, size=n) + 1e-9 # + min для > 0
        elif method == 'loguniform':
            # от 0.001 до 1
            weights = 10**np.random.uniform(-3, 0, size=n)
        else:
            raise ValueError("Метод должен быть 'uniform', 'exponential', 'dirichlet' или 'loguniform'")
        
        # Нормализуем веса, чтобы их сумма стала 1.0
        total_weight = np.sum(weights)
        if total_weight == 0: # Крайне маловероятный случай
            weights = np.ones(n)
            total_weight = n
            
        weights = weights / total_weight

    # --- 3. Распределение вероятностей ---
    # `probabilities` - это массив NumPy, который *точно* суммируется в 1.0
    # (в пределах машинной точности).
    # Каждому элементу даем "базу" min_prob, а остаток (scale_factor)
    # распределяем согласно `weights`.
    probabilities = min_prob + weights * scale_factor

    # --- 4. Округление с гарантией суммы 1.0 (Largest Remainder Method) ---
    multiplier = 10.0**decimals
    
    # Умножаем на 10^decimals и округляем *вниз*
    scaled_probs = probabilities * multiplier
    floored_probs = np.floor(scaled_probs)
    
    # Считаем, сколько "единиц" мы "потеряли" из-за округления вниз
    # (Например, 100.0 - (33.0 + 33.0 + 33.0) = 1.0)
    # Используем round() для устранения ошибок плавающей точки (np.sum может дать 9999.999...)
    total_floored_sum = np.sum(floored_probs)
    diff = int(round(multiplier - total_floored_sum))

    # `diff` - это количество элементов, которым нужно добавить 1 
    # (в нашем примере diff = 1)
    
    if diff > 0:
        # Находим остатки (дробные части)
        # (Например, [0.333..., 0.333..., 0.333...])
        remainders = scaled_probs - floored_probs
        
        # Находим индексы 'diff' *наибольших* остатков
        # (в примере это может быть любой из трех)
        indices_to_add = np.argsort(remainders)[-diff:]
        
        # Добавляем 1 к этим элементам
        # (Например, [33.0, 33.0, 33.0] -> [34.0, 33.0, 33.0])
        floored_probs[indices_to_add] += 1
    elif diff < 0:
        # Редкая ситуация, но возможная из-за ошибок float
        # Нужно *убавить* 1 у 'diff' *наименьших* остатков
        remainders = scaled_probs - floored_probs
        indices_to_remove = np.argsort(remainders)[:abs(diff)]
        floored_probs[indices_to_remove] -= 1

    # `final_probs_array` - это массив, где каждый элемент округлен
    # до `decimals` знаков, а их сумма *точно* равна 1.0
    final_probs_array = floored_probs / multiplier

    # --- 5. Создание словаря (Это самый медленный и "тяжелый" шаг) ---
    # Для n=1,000,000 этот шаг все равно может занять несколько секунд
    # и потребовать много памяти для *ключей*.
    
    # Генерируем ключи (быстрый способ)
    keys = (f'{prefix}{i+1}' for i in range(n))
    
    # `dict(zip(...))` - самый быстрый способ создать словарь из двух итераторов
    result = dict(zip(keys, final_probs_array))
    
    return result

# --- Пример использования ---
if __name__ == '__main__':
    
    # 1. Маленький пример для проверки суммы
    n_small = 3
    decimals_small = 2
    probs_small = generate_probabilities(n_small, 
                                         prefix='item', 
                                         method='uniform', 
                                         decimals=decimals_small)
    print(f"Пример для n={n_small}, decimals={decimals_small}:")
    print(probs_small)
    total_sum_small = sum(probs_small.values())
    print(f"Сумма: {total_sum_small} (Точно == 1.0: {total_sum_small == 1.0})")
    print("-" * 20)

    # 2. Большой пример для проверки производительности
    import time
    n_large = 1_000_000 # 1 миллион
    decimals_large = 6
    
    print(f"Генерация для n = {n_large:,}...")
    start_time = time.time()
    
    probs_large = generate_probabilities(n_large, 
                                         prefix='z', 
                                         method='dirichlet', 
                                         decimals=decimals_large,
                                         min_prob=1e-9) # 0.000000001
    
    end_time = time.time()
    print(f"Время генерации: {end_time - start_time:.4f} секунд")
    
    print("Проверка суммы для 1,000,000 элементов...")
    # Примечание: sum() для 1М элементов сам по себе может занять время
    start_sum_time = time.time()
    total_sum_large = sum(probs_large.values())
    end_sum_time = time.time()
    
    print(f"Время подсчета суммы: {end_sum_time - start_sum_time:.4f} секунд")
    print(f"Сумма: {total_sum_large}")
    
    # Проверка на ошибки округления (должно быть 0.0)
    print(f"Отклонение от 1.0: {abs(total_sum_large - 1.0)}")
    print(f"Точно == 1.0: {total_sum_large == 1.0}")
    
    # Проверка min_prob
    min_val = min(probs_large.values())
    print(f"Минимальная вероятность: {min_val} (>= 1e-9: {min_val >= 1e-9})")