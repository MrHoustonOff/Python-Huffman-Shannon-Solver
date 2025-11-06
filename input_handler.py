import math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()




HARDCODED_PROBS = {}
# HARDCODED_PROBS = {
#     'z1': 0.1, 'z2': 0.1, 'z3': 0.1, 'z4': 0.1, 'z5': 0.1,
#     'z6': 0.1, 'z7': 0.1, 'z8': 0.1, 'z9': 0.1, 'z10': 0.1
# }

# --- NEW HELPER FUNCTION ---
def _create_wide_table(probabilities: dict, num_cols: int = 5) -> Table:
    """
    Создает "широкую" таблицу вероятностей (5 столбцов)
    в формате:
    z1     | z2     | z3     | z4     | z5
    0.1000 | 0.1000 | 0.1000 | 0.1000 | 0.1000
    --------------------------------------------
    z6     | ...
    0.1000 | ...
    """
    
    table = Table(title="Введенные вероятности", padding=(0, 2), show_header=False)
    
    # Добавляем 5 пустых столбцов с центрированием
    for _ in range(num_cols):
        table.add_column(justify="center")

    # Сортируем ключи, чтобы z10 шел после z9
    sorted_keys = sorted(probabilities.keys(), key=lambda z: int(z[1:]))

    # Делим ключи на "чанки" (куски) по 5 штук
    chunks = []
    for i in range(0, len(sorted_keys), num_cols):
        chunks.append(sorted_keys[i : i + num_cols])
    
    # Теперь для каждого чанка (['z1', 'z2', 'z3', 'z4', 'z5']) добавляем 2 строки
    for chunk in chunks:
        # 1. Строка с именами
        symbol_row = [f"[cyan]{symbol}[/cyan]" for symbol in chunk]
        
        # 2. Строка с вероятностями
        prob_row = [f"[magenta]{probabilities[symbol]:.4f}[/magenta]" for symbol in chunk]
        
        # Добавляем их в таблицу. 
        # `add_row` автоматически заполнит пустые ячейки, если чанк неполный
        table.add_row(*symbol_row)
        table.add_row(*prob_row, end_section=True) # end_section=True добавит разделитель
        
    return table

def _show_hardcode_suggestion(probabilities: dict):
    """
    Показывает пользователю отформатированную строку
    для копирования в HARDCODED_PROBS.
    """
    
    # 1. Форматируем словарь в красивую строку
    # (Отсортируем по zN для консистентности)
    sorted_keys = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
    
    # Собираем внутренности словаря
    # 'z1': 0.1, 'z2': 0.1, ...
    items_str = ", ".join([f"'{key}': {probabilities[key]}" for key in sorted_keys])
    
    # Собираем финальную строку
    hardcode_string = f"HARDCODED_PROBS = {{ {items_str} }}"
    
    # 2. Выводим в красивой панельке
    rprint(
        Panel(
            f"[dim]Чтобы не вводить данные заново, скопируйте это\n"
            f"в начало файла [bold]input_handler.py[/bold]:[/dim]\n\n"
            f"[bold yellow]{hardcode_string}[/bold yellow]",
            title="💡 Подсказка",
            border_style="blue",
            padding=(1, 2)
        )
    )
    
# --- MODIFIED MAIN FUNCTION ---
def get_probabilities() -> dict:
    """
    Главная функция для ввода и валидации вероятностей.
    """
    
    while True:
        probabilities = {}
        rprint("\n" + "="*50)

        if HARDCODED_PROBS:
            rprint("[yellow]Обнаружены захардкоженные вероятности. Используем их... [/yellow]")
            rprint("[yellow]Если вы не согласны - замените константу на[/yellow] [red]HARDCODED_PROBS = {}[/red] [yellow]в файле[/yellow] [red]input_handler.py[/red]")
            probabilities = HARDCODED_PROBS
        else:
            rprint("[cyan]Режим ручного ввода.[/cyan] (введите [bold]-1[/bold] для завершения)")
            i = 1
            while True:
                try:
                    prob_str = console.input(f"  Введите вероятность для [bold]z{i}[/bold]: ")
                    if prob_str == '-1':
                        if not probabilities:
                            rprint("[red]Вы не ввели ни одной вероятности. Попробуйте снова.[/red]")
                            continue
                        break
                    prob = float(prob_str)
                    if not (0 < prob <= 1):
                        rprint("[red]Ошибка: Вероятность должна быть в интервале (0, 1].[/red]")
                        continue
                    probabilities[f'z{i}'] = prob
                    i += 1
                except ValueError:
                    rprint("[red]Ошибка: Введите число (например, 0.25).[/red]")
        
        if not probabilities:
            rprint("[red]Нет данных для обработки. Начинаем заново...[/red]\n")
            continue
		
        # 3.1. Проверка суммы
        total_prob = sum(probabilities.values())
        if math.isclose(total_prob, 1.0):
            rprint(f"\n[green]Сумма вероятностей: {total_prob:.4f} (Корректно!)[/green]")
            sum_ok = True
        else:
            rprint(f"\n[red]Сумма вероятностей: {total_prob:.4f} (ОШИБКА! Сумма не равна 1.0)[/red]")
            sum_ok = True

        # 3.2. Вывод таблицы для подтверждения
        rprint("[bold]Вот ваши вероятности:[/bold]")
        
        # --- MODIFIED BLOCK ---
        # Старая таблица удалена. Вызываем новую функцию.
        table = _create_wide_table(probabilities, num_cols=5)
        console.print(table)
        # --- END MODIFIED BLOCK ---

        # 3.3. Подтверждение пользователя
        choice = console.input("Все верно? ([bold green]1[/bold green] - да / [bold red]0[/bold red] - нет): ")

        if choice == '1':
            if sum_ok:
                rprint("[bold green]Вероятности приняты. Продолжаем...[/bold green]")
                if not HARDCODED_PROBS: # Показываем, только если вводили вручную
                    _show_hardcode_suggestion(probabilities)
                sorted_keys = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
                return {symbol: probabilities[symbol] for symbol in sorted_keys}
            else:
                rprint("[red]Вы подтвердили, но сумма не равна 1.0. Пожалуйста, введите данные заново.[/red]\n")
        elif choice == '0':
            rprint("[yellow]Перевводим...[/yellow]\n")
        else:
            rprint("[red]Неверный ввод. Пожалуйста, введите 1 или 0.[/red]\n")

if __name__ == "__main__":
    rprint("[bold blue]Запуск модуля ввода данных (с новой широкой таблицей)...[/bold blue]")
    
    # --- Чтобы протестировать ручной ввод, ---
    # --- убедитесь, что HARDCODED_PROBS = {} ---
    
    final_probabilities = get_probabilities()
    
    rprint("\n[bold]Основная программа (main.py) получила данные:[/bold]")
    console.print(final_probabilities)