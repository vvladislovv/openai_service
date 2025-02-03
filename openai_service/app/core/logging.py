from app.db.database import add_to_table, JsonData


async def logs_bot(TypeLog: str, Text: str) -> None:
    """
    Логирует сообщения в базу данных.

    Аргументы:
        TypeLog: str - Уровень логирования (например, "error", "warning", "info", "debug").
        Text: str - Сообщение для логирования.
    """
    valid_log_types = ["error", "warning", "info", "debug"]
    if TypeLog.lower() not in valid_log_types:
        TypeLog = "warning"  

    # Сохраняем лог в базу данных
    log_entry = JsonData(data={"level": TypeLog, "message": Text})
    await add_to_table(JsonData, {"data": log_entry.data})  # Оборачиваем log_entry.data в словарь
