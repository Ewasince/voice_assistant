from agents import function_tool


@function_tool()
def f2c(f: float) -> float:
    """Конвертирует температуру из °F в °C. Используй, когда просят перевести Фаренгейт в Цельсий."""
    print("tool called!")
    return (f - 32) * 5.0 / 9.0
