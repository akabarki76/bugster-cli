"""
Destructive agent limit logic for Bugster CLI
"""

from collections import defaultdict
from typing import List, Optional, Tuple


# Agent priority order (higher number = higher priority)
AGENT_PRIORITIES = {
    "UI Crashers": 2,
    "From Destroyer": 1,
}


def apply_destructive_agent_limit(
    page_agent_tuples: List[Tuple[str, str, str]], max_agents: Optional[int] = None
) -> Tuple[List[Tuple[str, str, str]], dict]:
    """
    Apply destructive agent limit logic to select a representative subset of agents.

    Args:
        page_agent_tuples: List of (page, agent, diff) tuples
        max_agents: Maximum number of agents to run (if None, no limit)

    Returns:
        Tuple of (limited list of agent tuples, agent type distribution dict)
    """
    if max_agents is None:
        return page_agent_tuples, {}

    total_agents = len(page_agent_tuples)

    if total_agents <= max_agents:
        return page_agent_tuples, {}

    # Group agents by type and apply prioritization
    selected_agents, agent_distribution = select_prioritized_agents(
        page_agent_tuples, max_agents
    )

    return selected_agents, agent_distribution


def group_agents_by_type(
    page_agent_tuples: List[Tuple[str, str, str]]
) -> dict[str, List[Tuple[str, str, str]]]:
    """
    Group agents by their type.

    Args:
        page_agent_tuples: List of (page, agent, diff) tuples

    Returns:
        Dictionary mapping agent types to lists of agent tuples
    """
    agent_groups = defaultdict(list)

    for page, agent, diff in page_agent_tuples:
        # Determine agent type based on agent name
        agent_type = get_agent_type(agent)
        agent_groups[agent_type].append((page, agent, diff))

    return dict(agent_groups)


def get_agent_type(agent_name: str) -> str:
    """
    Determine agent type from agent name.

    Args:
        agent_name: Name of the agent

    Returns:
        Agent type string
    """
    # Map agent names to types based on known patterns
    if "UI Crashers" in agent_name or "ui_crasher" in agent_name.lower():
        return "UI Crashers"
    elif "From Destroyer" in agent_name or "destroyer" in agent_name.lower():
        return "From Destroyer"
    else:
        # Unknown agent type gets lowest priority
        return "Other"


def select_prioritized_agents(
    page_agent_tuples: List[Tuple[str, str, str]], max_agents: int
) -> Tuple[List[Tuple[str, str, str]], dict]:
    """
    Select agents based on strict priority order: ALL UI Crashers first, then From Destroyer, then Others.

    Args:
        page_agent_tuples: List of (page, agent, diff) tuples
        max_agents: Maximum number of agents to select

    Returns:
        Tuple of (list of selected agent tuples, agent type distribution dict)
    """
    # Group agents by type
    agent_groups = group_agents_by_type(page_agent_tuples)
    
    if not agent_groups:
        return [], {}

    # Sort agent types by priority (highest first)
    sorted_agent_types = sorted(
        agent_groups.keys(),
        key=lambda x: AGENT_PRIORITIES.get(x, 0),
        reverse=True
    )

    selected_agents = []
    agent_distribution = {}
    remaining_slots = max_agents

    # Select ALL agents from each type in strict priority order
    for agent_type in sorted_agent_types:
        if remaining_slots <= 0:
            break
            
        available_agents = agent_groups[agent_type]
        
        # Take as many agents as possible from this type (up to remaining slots)
        agents_to_take = min(len(available_agents), remaining_slots)
        
        if agents_to_take > 0:
            selected_agents.extend(available_agents[:agents_to_take])
            agent_distribution[agent_type] = agents_to_take
            remaining_slots -= agents_to_take

    return selected_agents[:max_agents], agent_distribution


def count_total_agents(page_agent_tuples: List[Tuple[str, str, str]]) -> int:
    """
    Count total number of destructive agents.

    Args:
        page_agent_tuples: List of (page, agent, diff) tuples

    Returns:
        Total number of agents
    """
    return len(page_agent_tuples)


def get_destructive_limit_from_config() -> Optional[int]:
    """
    Get destructive agent limit from configuration.

    Returns:
        Maximum number of agents to run, or None if no limit
    """
    try:
        from bugster.utils.file import load_config

        config = load_config()

        # Check if limit is configured in preferences.destructive_limit
        if (
            config.preferences 
            and hasattr(config.preferences, 'destructive_limit') 
            and config.preferences.destructive_limit is not None
        ):
            return config.preferences.destructive_limit

        # Default limit for destructive agents
        return 2
    except Exception:
        # If config loading fails, return default
        return 2