def format_tests_for_llm(
    existing_specs: list[dict] | dict, include_page_path: bool = False
) -> str:
    """Format a list of specs for LLM context to prevent duplication.

    :param existing_specs: Dict or list of dicts with the spec data.
    :return: Formatted context string for LLM.
    """
    context_lines = []

    if isinstance(existing_specs, list):
        for i, spec in enumerate(existing_specs, 1):
            if include_page_path:
                page_path = spec["data"]["page_path"]
                context_lines.append(f"Page: {page_path}")

            name = spec["data"]["name"]
            task = spec["data"]["task"]
            steps = " -> ".join(spec["data"]["steps"])
            context_lines.append(
                f"{i}. Test: {name}. Task: {task.lower()}. Steps: {steps}"
            )
    elif isinstance(existing_specs, dict):
        if include_page_path:
            page_path = existing_specs["data"]["page_path"]
            context_lines.append(f"Page: {page_path}")

        name = existing_specs["data"]["name"]
        task = existing_specs["data"]["task"]
        steps = " -> ".join(existing_specs["data"]["steps"])
        context_lines.append(f"Test: {name}. Task: {task.lower()}. Steps: {steps}")
    else:
        raise ValueError("Invalid existing specs type")

    return "\n".join(context_lines)
