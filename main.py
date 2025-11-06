import math
from typing import Dict, List
from pathlib import Path  # <-- ИМПОРТ ДЛЯ РАБОТЫ С ПУТЯМИ

# --- Импорты наших модулей ---
import input_handler
import algorithms
import metrics
import visualizer
from metrics import ROUND_DIGITS

# --- Импорты для "красоты" ---
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

# --- Константы ---
console = Console()
ALGORITHMS = {
    "1": "Хаффман",
    "2": "Шеннон-Фано",
}


def _build_codes_table(
    probabilities: Dict[str, float],
    generated_codes: Dict[str, str],
    symbols_list: List[str],
    title: str
) -> Table:
    """
    Вспомогательная функция для создания итоговых таблиц с кодами.

    Args:
        probabilities (dict): Словарь вероятностей {'z1': p1, ...}.
        generated_codes (dict): Словарь кодов {'z1': '01', ...}.
        symbols_list (list): Отсортированный список символов для вывода.
        title (str): Заголовок для таблицы.

    Returns:
        Table: Готовый объект Table от 'rich'.
    """
    
    table = Table(title=title)
    table.add_column("Символ (z)", style="cyan", no_wrap=True)
    table.add_column("Вероятность (p)", style="magenta")
    table.add_column("Кодовое слово", style="yellow")
    table.add_column("Длина (L)", style="green", justify="right")
    
    for symbol in symbols_list:
        prob = probabilities[symbol]
        code = generated_codes.get(symbol, "Н/Д")
        length = len(code)
        
        table.add_row(
            symbol,
            f"{prob:.{ROUND_DIGITS}f}",
            code,
            str(length)
        )
    return table


def select_algorithm(previous_algo_name: str = None) -> str | None:
    """
    Отображает меню выбора алгоритма.

    Args:
        previous_algo_name (str, optional): Имя последнего запущенного алгоритма.

    Returns:
        str | None: Имя выбранного алгоритма или None для выхода.
    """
    rprint("\n" + "="*50)
    console.print("[bold]Выберите алгоритм для расчета:[/bold]")
    
    options = {}
    
    if previous_algo_name:
        # Режим "повторного запуска"
        other_algo_key = "2" if previous_algo_name == "Хаффман" else "1"
        other_algo_name = ALGORITHMS[other_algo_key]
        
        console.print(f"[bold green] [1] Рассчитать также для {other_algo_name}[/bold green]")
        console.print(f" [2] Рассчитать еще раз для {previous_algo_name}")
        
        options = {
            "1": other_algo_name,
            "2": previous_algo_name,
            "0": None  # Выход
        }
    else:
        # Режим "первого запуска"
        console.print(f" [1] {ALGORITHMS['1']}")
        console.print(f" [2] {ALGORITHMS['2']}")
        options = {
            "1": ALGORITHMS['1'],
            "2": ALGORITHMS['2'],
            "0": None  # Выход
        }
        
    console.print(f" [0] Выход из программы")
    
    while True:
        choice = console.input(f"Введите (0-{len(options)-1}): ")
        if choice in options:
            return options[choice]
        else:
            rprint("[red]Неверный ввод, попробуйте снова.[/red]")


def run_calculation_flow(algo_name: str, probabilities: Dict[str, float], output_path: Path):
    """
    Запускает полный цикл расчета (Шаги 2-5) для выбранного алгоритма.

    Args:
        algo_name (str): Имя алгоритма ("Хаффман" или "Шеннон-Фано").
        probabilities (dict): Провалидированный словарь вероятностей.
        output_path (Path): Путь к папке (напр. "results/output_1").
    """
    
    rprint(
        Panel(
            f"[bold white on blue] --- {algo_name.upper()} --- [/bold white on blue]",
            expand=False,
            padding=(0, 10)
        )
    )

    # Шаг 2: Построение дерева
    rprint(f"\n[bold blue]Шаг 2 ({algo_name}): Построение дерева...[/bold blue]")
    tree_root = None
    try:
        if algo_name == "Хаффман":
            tree_root = algorithms.build_huffman_tree(probabilities)
        elif algo_name == "Шеннон-Фано":
            tree_root = algorithms.build_shannon_fano_tree(probabilities)
            
        if tree_root is None:
             rprint("[bold red]Ошибка: Не удалось построить дерево.[/bold red]")
             return
        rprint("[green]...Дерево успешно построено.[/green]")
        
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при построении дерева ({algo_name}): {e}[/bold red]")
        return

    # Шаг 3: Генерация кодов и Визуализация
    rprint(f"\n[bold blue]Шаг 3 ({algo_name}): Генерация кодов и изображений...[/bold blue]")
    generated_codes = {}
    try:
        rprint("[dim]...Генерируем коды из дерева...[/dim]")
        generated_codes = algorithms.generate_codes_from_tree(tree_root)
        rprint("[green]...Коды успешно сгенерированы.[/green]")
        
        rprint("[dim]...Запускаем генерацию изображений...[/dim]")
        # --- ИЗМЕНЕНО: Передаем 'str(output_path)' ---
        if algo_name == "Хаффман":
            visualizer.generate_scheme_image(tree_root, algo_name, str(output_path))
            visualizer.generate_classic_tree_image(tree_root, algo_name, str(output_path))
        elif algo_name == "Шеннон-Фано":
            visualizer.generate_classic_tree_image(tree_root, algo_name, str(output_path))
            
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка на Шаге 3: {e}[/bold red]")
        return

    # Шаг 4: Расчет метрик ("Матан")
    rprint(f"\n[bold blue]Шаг 4 ({algo_name}): Расчет метрик...[/bold blue]")
    try:
        h_result, h_gen, h_exp, h_sub = metrics.calculate_entropy(probabilities)
        console.print(Panel(f"[dim]{h_gen}[/dim]\n[dim]{h_exp}[/dim]\n{h_sub}\n\n[bold]H = {h_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {h_result})[/dim]", title=f"[bold yellow]H (Энтропия)[/bold yellow]", border_style="yellow", padding=(1, 2)))

        l_result, l_gen, l_exp, l_sub = metrics.calculate_average_length(probabilities, generated_codes)
        console.print(Panel(f"[dim]{l_gen}[/dim]\n[dim]{l_exp}[/dim]\n{l_sub}\n\n[bold]L_avg = {l_result:.{ROUND_DIGITS}f} бит/символ[/bold] [dim]| (raw: {l_result})[/dim]", title=f"[bold green]L_avg (Средняя длина)[/bold green]", border_style="green", padding=(1, 2)))
        
        r_result, r_gen, r_sub = metrics.calculate_redundancy(l_result, h_result)
        console.print(Panel(f"[dim]{r_gen}[/dim]\n{r_sub}\n\n[bold]r = {r_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {r_result})[/dim]", title=f"[bold cyan]r (Избыточность)[/bold cyan]", border_style="cyan", padding=(1, 2)))

        k_result, k_gen, k_exp, k_sub = metrics.calculate_kraft_inequality(generated_codes)
        raw_k_str = f"[dim]| (raw: {k_result})[/dim]" if not math.isclose(k_result, 1.0) else ""
        if math.isclose(k_result, 1.0) or k_result < 1.0:
            kraft_status = (f"[bold green]K = {k_result:.{ROUND_DIGITS}f} (≤ 1.0)[/bold green] {raw_k_str}\n[green]Неравенство выполняется, код однозначно декодируем.[/green]")
        else:
            kraft_status = (f"[bold red]K = {k_result:.{ROUND_DIGITS}f} (> 1.0)[/bold red] {raw_k_str}\n[red]Ошибка! Код НЕ является однозначно декодируемым.[/red]")
        console.print(Panel(f"[dim]{k_gen}[/dim]\n[dim]{k_exp}[/dim]\n{k_sub}\n\n{kraft_status}", title=f"[bold magenta]K (Неравенство Крафта)[/bold magenta]", border_style="magenta", padding=(1, 2)))
    
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при расчете метрик ({algo_name}): {e}[/bold red]")


    # Шаг 5: Вывод итоговых таблиц
    rprint(f"\n[bold blue]Шаг 5 ({algo_name}): Итоговые коды[/bold blue]")
    
    sorted_by_prob = sorted(probabilities.keys(), key=lambda symbol: probabilities[symbol], reverse=True)
    table1 = _build_codes_table(probabilities, generated_codes, sorted_by_prob, f"[bold]Коды ({algo_name}) (отсортировано по P ↓)[/bold]")
    console.print(table1)

    sorted_by_name = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
    table2 = _build_codes_table(probabilities, generated_codes, sorted_by_name, f"[bold]Коды ({algo_name}) (отсортировано по Z ↑)[/bold]")
    console.print(table2)


# --- НОВАЯ ФУНКЦИЯ СОЗДАНИЯ ПАПОК ---
def setup_output_directory(base_dir: str = "results") -> Path:
    """
    Создает (если нет) папку `results` и в ней
    уникальную папку `output_N` для этого запуска.

    Args:
        base_dir (str): Имя корневой папки для результатов.

    Returns:
        Path: Объект Path, указывающий на "results/output_N".
    """
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True) # Гарантируем, что 'results' существует

    # Ищем существующие папки 'output_N'
    existing_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("output_")]
    
    max_n = 0
    for d in existing_dirs:
        try:
            # Извлекаем 'N' из 'output_N'
            n = int(d.name.split('_')[-1])
            if n > max_n:
                max_n = n
        except ValueError:
            continue # Игнорируем 'output_final' или 'output_test'
    
    next_n = max_n + 1
    new_dir_path = base_path / f"output_{next_n}"
    new_dir_path.mkdir()
    
    return new_dir_path


def main():
    """
    Главная "оркестровая" функция программы.
    """
    rprint("[bold green]Запуск программы кодирования...[/bold green]")
    rprint("="*50)

    # Шаг 1: Получение данных (Один раз)
    rprint("[bold blue]Шаг 1: Ввод данных...[/bold blue]")
    probabilities = input_handler.get_probabilities()
    if not probabilities:
        rprint("[bold red]Ошибка: Вероятности не получены. Выход.[/bold red]")
        return

    # --- ИЗМЕНЕНО: Создаем папку для вывода ---
    try:
        output_dir = setup_output_directory()
        console.print(f"[bold green]Создана директория для результатов: [cyan]{output_dir}[/cyan][/bold green]")
    except Exception as e:
        rprint(f"[bold red]Не удалось создать папку для результатов: {e}[/bold red]")
        rprint("[red]Изображения будут сохранены в корневой папке.[/red]")
        output_dir = Path(".") # Сохраняем в текущую папку как запасной вариант

    # Главный цикл (Запуск алгоритмов)
    last_algo_run = None
    while True:
        algo_to_run = select_algorithm(last_algo_run)
        
        if algo_to_run is None:
            break
            
        # --- ИЗМЕНЕНО: Передаем 'output_dir' ---
        run_calculation_flow(algo_to_run, probabilities, output_dir)
        
        last_algo_run = algo_to_run

    rprint("\n[bold green]Программа завершена. Удачной атты![/bold green]")


if __name__ == "__main__":
    print(
        r'''
<-. (`-')     (`-')  (`-').->                       (`-').->(`-')                <-. (`-')_ 
   \(OO )_ <-.(OO )  (OO )__      .->        .->    ( OO)_  ( OO).->       .->      \( OO) )
,--./  ,-.),------,),--. ,'-'(`-')----. ,--.(,--.  (_)--\_) /    '._  (`-')----. ,--./ ,--/ 
|   `.'   ||   /`. '|  | |  |( OO).-.  '|  | |(`-')/    _ / |'--...__)( OO).-.  '|   \ |  | 
|  |'.'|  ||  |_.' ||  `-'  |( _) | |  ||  | |(OO )\_..`--. `--.  .--'( _) | |  ||  . '|  |)
|  |   |  ||  .   .'|  .-.  | \|  |)|  ||  | | |  \.-._)   \   |  |    \|  |)|  ||  |\    | 
|  |   |  ||  |\  \ |  | |  |  '  '-'  '\  '-'(_ .'\       /   |  |     '  '-'  '|  | \   | 
`--'   `--'`--' '--'`--' `--'   `-----'  `-----'    `-----'    `--'      `-----' `--'  `--' 
''')
    main()