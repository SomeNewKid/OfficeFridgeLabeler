from __future__ import annotations

from datetime import date, timedelta

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Pretend Office MCP Server")

SHARED_FOOD_RULES = """
# Shared Food Rules

This resource defines the office fridge treaty.

## Core principles

1. Label anything that is not obviously communal.
2. Do not eat food with someone else's name on it.
3. Do not assume unlabelled food is free.
4. Strong-smelling food must be sealed.
5. Expired food may be removed during the Friday fridge reset.
6. Communal food must be clearly marked as communal.
7. Mystery containers are not to be opened for investigation unless they are leaking,
   expanding, or making threats.

## Label requirements

A valid fridge label should include:

- Item name
- Owner name
- Expiry or removal date
- Whether the item is private, communal, or mystery
- Optional warning, such as "contains nuts", "very spicy", or "do not microwave"

## Default expiry rules

Use these defaults when no expiry date is supplied:

- Cooked meal: 3 days
- Dairy item: 5 days
- Salad: 2 days
- Sauce or condiment: 30 days
- Cake, biscuits, or snacks: 5 days
- Mystery container: 1 day
- Clearly labelled communal food: 2 days
- Sealed commercial drink: 14 days

## Friday fridge reset

Every Friday afternoon, expired items may be removed.

Items without a label may be removed if they appear old, unsafe, or leaking.

Communal items should be removed if they are past their communal expiry date.

## Tone

Labels should be clear, polite, and faintly dramatic.

Acceptable:
- "Private lunch. Please admire from a distance."
- "Communal cake. Take one piece. Leave hope for others."
- "Expires Friday. After that, it joins the compost."

Not acceptable:
- Direct accusations
- Threats
- Passive-aggressive essays
- Labels longer than the container
""".strip()


@mcp.resource("fridge://shared-food-rules")
def shared_food_rules() -> str:
    """Return the rules of using the office fridge"""
    return SHARED_FOOD_RULES


@mcp.tool()
def generate_fridge_label(item: str, owner: str, expiry: str = "") -> str:
    """
    Generate a fridge label.

    Args:
        item: The food or container being labelled.
        owner: The person or group responsible for the item.
        expiry: Optional expiry/removal date in YYYY-MM-DD format.
            If omitted, a default is chosen from the item description.
    """
    if not item:
        raise ValueError("item must not be empty")

    if not owner:
        raise ValueError("owner must not be empty")

    category = _guess_category(item, owner)
    warnings = _guess_warnings(item)
    remove_after = expiry.strip() or _default_remove_after(item)

    return _build_label_text(item, owner, category, remove_after, warnings)


def _guess_category(item: str, owner: str) -> str:
    text = f"{item} {owner}".lower()

    if "communal" in text or "shared" in text:
        return "communal"

    if "unknown" in text or "mystery" in text or "unidentified" in text:
        return "mystery"

    return "private"


def _guess_warnings(item: str) -> list[str]:
    text = item.lower()
    warnings: list[str] = []

    if any(word in text for word in ["fish", "tuna", "sardine", "stew", "curry"]):
        warnings.append("seal properly")

    if any(word in text for word in ["spicy", "chilli", "chili", "hot sauce"]):
        warnings.append("spicy")

    if any(word in text for word in ["nut", "peanut", "almond", "cashew"]):
        warnings.append("contains nuts")

    return warnings


def _default_remove_after(item: str) -> str:
    text = item.lower()

    days = 3  # default cooked meal

    if any(word in text for word in ["salad", "lettuce", "slaw"]):
        days = 2
    elif any(word in text for word in ["milk", "cheese", "yoghurt", "yogurt", "cream"]):
        days = 5
    elif any(word in text for word in ["sauce", "condiment", "pickle", "jam"]):
        days = 30
    elif any(word in text for word in ["cake", "biscuit", "cookie", "snack"]):
        days = 5
    elif any(word in text for word in ["mystery", "unknown", "unidentified"]):
        days = 1
    elif any(word in text for word in ["drink", "can", "bottle", "juice"]):
        days = 14
    elif "communal" in text or "shared" in text:
        days = 2

    return (date.today() + timedelta(days=days)).isoformat()


def _build_label_text(
    item: str,
    owner: str,
    category: str,
    remove_after: str,
    warnings: list[str],
) -> str:
    category_heading = {
        "private": "PRIVATE FOOD",
        "communal": "COMMUNAL FOOD",
        "mystery": "MYSTERY ITEM",
    }.get(category, "FRIDGE ITEM")

    lines = [
        category_heading,
        f"Item: {item}",
        f"Owner: {owner}",
        f"Remove after: {remove_after}",
    ]

    if warnings:
        lines.append(f"Warning: {', '.join(warnings)}.")

    if category == "communal":
        lines.append("Note: Take one piece. Leave civilisation intact.")
    elif category == "mystery":
        lines.append("Note: Do not open unless leaking, expanding, or making threats.")
    else:
        lines.append("Note: Please admire from a distance.")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
