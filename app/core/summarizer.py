def summarize(text: str) -> dict:
    """
    Stage 5 stub.
    Returns:
      summary: str
      tasks: list[dict]
    """
    summary = text.strip()

    tasks = [{
        "title": text[:60],
        "description": text,
    }]

    return {
        "summary": summary,
        "tasks": tasks
    }
