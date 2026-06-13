"""Command-line interface for Office Fridge Labeler."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

RESOURCE_URI = "fridge://shared-food-rules"


def run() -> None:
    """Run the command-line interface."""
    asyncio.run(main())


async def main() -> None:
    """Run the command-line interface."""
    args = _parse_args()

    async with MCPServerStdio(
        name="Pretend Office MCP Server",
        params={
            "command": sys.executable,
            "args": ["-m", "office_fridge_labeler.mcp_server"],
        },
        cache_tools_list=True,
    ) as server:
        food_rules_resource = await server.read_resource(RESOURCE_URI)
        food_rules_text = _extract_resource_text(food_rules_resource)

        agent = Agent(
            name="Office Fridge Labeling Agent",
            instructions=f"""
You are the Office Fridge Labeling Agent.

Your job is to create exactly one office fridge label.

You have been given the office fridge food rules below. Use it as policy context.

OFFICE FRIDGE FOOD RULES:
{food_rules_text}

Rules for this run:

1. Extract the food item, owner, and expiry/removal date from the user's request.
2. If the user does not provide an expiry/removal date, pass an empty string.
3. You must call the MCP tool named generate_fridge_label.
4. Your final answer must be only the label_text returned by the tool.
5. Do not add explanation, markdown fences, commentary, or extra text.
""".strip(),
            mcp_servers=[server],
        )

        result = await Runner.run(agent, args.request)

    print(result.final_output)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Office Fridge Labeler.",
    )
    parser.add_argument("request")
    return parser.parse_args()


def _extract_resource_text(resource_result: Any) -> str:
    """
    Extract text from an MCP ReadResourceResult.

    MCP resource results usually contain a `contents` list.
    Text resources expose `.text`.
    """
    contents = getattr(resource_result, "contents", None)

    if not contents:
        raise RuntimeError("MCP resource returned no contents.")

    chunks: list[str] = []

    for content in contents:
        text = getattr(content, "text", None)
        if text is not None:
            chunks.append(text)

    if not chunks:
        raise RuntimeError("MCP resource did not contain text content")

    return "\n".join(chunks)
