import math
from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from random_probs import generate_probabilities # (Предполагаем, что random_probs.py у тебя есть)

# --- Глобальные переменные ---
console = Console()

# Порог, после которого отключается "раскошный" вывод
LARGE_INPUT_THRESHOLD = 100

# Оставьте словарь пустым ({}), чтобы включить ручной ввод.
HARDCODED_PROBS = {}

# Раскомментируйте эту строку для теста с N-ым кол-вом случайных величин
HARDCODED_PROBS = generate_probabilities(3000, 
                                         prefix='z', 
                                         method='dirichlet', 
                                         decimals=6,
                                         min_prob=1e-9)


def _create_wide_table(probabilities: Dict[str, float], num_cols: int = 5) -> Table:
    """
    Создает "широкую" таблицу вероятностей (N столбцов)
    в удобном для чтения формате (Имя_zN, затем P_zN).

    Args:
        probabilities (dict): Словарь с вероятностями {'z1': 0.1, ...}.
        num_cols (int): Количество столбцов в таблице.

    Returns:
        Table: Готовый объект Table от 'rich' для вывода.
    """
    
    table = Table(title="Введенные вероятности", padding=(0, 2), show_header=False)
    
    for _ in range(num_cols):
        table.add_column(justify="center")

    sorted_keys = sorted(probabilities.keys(), key=lambda z: int(z[1:]))

    chunks = []
    for i in range(0, len(sorted_keys), num_cols):
        chunks.append(sorted_keys[i : i + num_cols])
    
    for chunk in chunks:
        symbol_row = [f"[cyan]{symbol}[/cyan]" for symbol in chunk]
        prob_row = [f"[magenta]{probabilities[symbol]:.4f}[/magenta]" for symbol in chunk]
        
        table.add_row(*symbol_row)
        table.add_row(*prob_row, end_section=True)
        
    return table

def _show_hardcode_suggestion(probabilities: Dict[str, float]):
    """
    Показывает пользователю отформатированную строку
    для копирования в HARDCODED_PROBS в коде.
    
    Args:
        probabilities (dict): Словарь с вероятностями {'z1': 0.1, ...}.
    """
    
    sorted_keys = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
    
    items_str = ", ".join([f"'{key}': {probabilities[key]}" for key in sorted_keys])
    
    hardcode_string = f"HARDCODED_PROBS = {{ {items_str} }}"
    
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
    
def get_probabilities() -> Dict[str, float]:
    """
    Главная функция для ввода и валидации вероятностей.
    
    Сначала проверяет HARDCODED_PROBS. Если они есть,
    предлагает выбор: использовать их или перейти к ручному вводу.
    Циклически запрашивает ввод, пока данные не будут подтверждены.

    Returns:
        dict: Провалидированный словарь с вероятностями {'z1': 0.1, ...}.
    """
    
    while True:
        probabilities = {}
        rprint("\n" + "="*50)

        if HARDCODED_PROBS:
            rprint("[yellow]Обнаружены захардкоженные вероятности.[/yellow]")
            console.print(" [1] Использовать захардкоженные")
            console.print(" [2] Перейти к ручному вводу")
            choice = console.input("Ваш выбор (1/2): ")
            
            if choice == '1':
                rprint("[yellow]Используем захардкоженные...[/yellow]")
                probabilities = HARDCODED_PROBS
            elif choice == '2':
                rprint("[cyan]Переходим к ручному вводу...[/cyan]")
                pass
            else:
                rprint("[red]Неверный ввод. Пожалуйста, выберите 1 или 2.[/red]")
                continue # Перезапускаем цикл
        
        # Ручной ввод запускается, если:
        # 1. HARDCODED_PROBS пуст
        # 2. HARDCODED_PROBS есть, но пользователь выбрал [2]
        if not probabilities:
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
        
        # Проверка на N > 100
        N = len(probabilities)
        is_large_input = (N > LARGE_INPUT_THRESHOLD)
        
        # Проверка суммы
        total_prob = sum(probabilities.values())
        if math.isclose(total_prob, 1.0):
            rprint(f"\n[green]Сумма вероятностей: {total_prob:.4f} (Корректно!)[/green]")
            sum_ok = True
        else:
            rprint(f"\n[red]Сумма вероятностей: {total_prob:.4f} (ОШИБКА! Сумма не равна 1.0)[/red]")
            sum_ok = False

        # Вывод таблицы для подтверждения (только если N не слишком большое)
        if not is_large_input:
            rprint("[bold]Вот ваши вероятности:[/bold]")
            table = _create_wide_table(probabilities, num_cols=5)
            console.print(table)
        else:
            rprint(f"[yellow]Ввод (N={N}) слишком большой для отображения таблицы.[/yellow]")

        # Подтверждение пользователя
        choice = console.input("Все верно? ([bold green]1[/bold green] - да / [bold red]0[/bold red] - нет): ")

        if choice == '1':
            if sum_ok:
                rprint("[bold green]Вероятности приняты. Продолжаем...[/bold green]")
                # Показываем подсказку, только если вводили вручную И N не слишком большое
                if not HARDCODED_PROBS and not is_large_input:
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
    """
    Тестовый запуск для проверки этого модуля.
    """
    rprint("[bold blue]Запуск модуля ввода данных...[/bold blue]")
    
    final_probabilities = get_probabilities()
    
    rprint("\n[bold]Основная программа (main.py) получила данные:[/bold]")
    console.print(f"Получено {len(final_probabilities)} символов.")
    if len(final_probabilities) <= 20:
        console.print(final_probabilities)