"""Browser MCP tool implementation."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, override

from kosong.tooling import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field

from kimi_cli.soul.agent import Runtime
from kimi_cli.tools.utils import ToolResultBuilder, load_desc
from kimi_cli.utils.logging import logger


class BrowserNavigateParams(BaseModel):
    """Parameters for browser navigation."""

    url: str = Field(description="The URL to navigate to")


class BrowserSnapshotParams(BaseModel):
    """Parameters for browser snapshot."""

    pass


class BrowserClickParams(BaseModel):
    """Parameters for browser click."""

    element: str = Field(description="Human-readable element description")
    ref: str = Field(description="Exact target element reference from the page snapshot")
    button: str = Field(default="left", description="Button to click (left, right, middle)")
    doubleClick: bool = Field(default=False, description="Whether to perform a double click")
    modifiers: list[str] = Field(default_factory=list, description="Modifier keys to press")


class BrowserTypeParams(BaseModel):
    """Parameters for browser type."""

    element: str = Field(description="Human-readable element description")
    ref: str = Field(description="Exact target element reference from the page snapshot")
    text: str = Field(description="Text to type into the element")
    submit: bool = Field(default=False, description="Whether to submit entered text (press Enter)")
    slowly: bool = Field(
        default=False, description="Whether to type one character at a time"
    )


class BrowserScreenshotParams(BaseModel):
    """Parameters for browser screenshot."""

    filename: str | None = Field(default=None, description="File name to save the screenshot to")
    fullPage: bool = Field(default=False, description="Take screenshot of full scrollable page")
    element: str | None = Field(default=None, description="Description of element to screenshot")
    ref: str | None = Field(default=None, description="CSS selector for element screenshot")


class BrowserTool:
    """Browser automation tool using Chrome DevTools MCP."""

    def __init__(self, runtime: Runtime):
        """Initialize browser tool with runtime context."""
        self._runtime = runtime
        self._mcp_client: Any | None = None
        self._mcp_process: subprocess.Popen | None = None

    async def _ensure_mcp_client(self) -> Any:
        """Ensure MCP client is initialized."""
        if self._mcp_client is not None:
            return self._mcp_client

        try:
            import fastmcp

            # Create MCP config for chrome-devtools-mcp
            mcp_config = {
                "mcpServers": {
                    "chrome-devtools": {
                        "command": "npx",
                        "args": ["-y", "chrome-devtools-mcp@latest"],
                    }
                }
            }

            logger.info("Initializing Chrome DevTools MCP client")
            client = fastmcp.Client(mcp_config)
            self._mcp_client = client
            return client
        except Exception as e:
            logger.exception("Failed to initialize MCP client: {error}", error=e)
            raise

    async def _call_mcp_tool(self, tool_name: str, params: dict[str, Any]) -> ToolReturnValue:
        """Call an MCP tool and return the result."""
        try:
            client = await self._ensure_mcp_client()
            async with client:
                result = await client.call_tool(tool_name, params, timeout=60, raise_on_error=False)

                builder = ToolResultBuilder()
                if result.is_error:
                    builder.write(f"Error: {result.content}")
                    return builder.error(
                        f"MCP tool {tool_name} returned an error",
                        brief="MCP tool error",
                    )

                # Convert MCP result to text
                content_parts = []
                for part in result.content:
                    if hasattr(part, "text"):
                        content_parts.append(part.text)
                    else:
                        content_parts.append(str(part))

                output = "\n".join(content_parts) if content_parts else "Success"
                builder.write(output)
                return builder.ok(f"Browser operation {tool_name} completed successfully")
        except Exception as e:
            logger.exception("Error calling MCP tool {tool}: {error}", tool=tool_name, error=e)
            return ToolError(
                output=str(e),
                message=f"Failed to execute browser operation: {e}",
                brief="Browser operation failed",
            )

    async def navigate(self, params: BrowserNavigateParams) -> ToolReturnValue:
        """Navigate to a URL."""
        return await self._call_mcp_tool("browser_navigate", {"url": params.url})

    async def snapshot(self, params: BrowserSnapshotParams) -> ToolReturnValue:
        """Get page snapshot."""
        return await self._call_mcp_tool("browser_snapshot", {})

    async def click(self, params: BrowserClickParams) -> ToolReturnValue:
        """Click on an element."""
        return await self._call_mcp_tool(
            "browser_click",
            {
                "element": params.element,
                "ref": params.ref,
                "button": params.button,
                "doubleClick": params.doubleClick,
                "modifiers": params.modifiers,
            },
        )

    async def type_text(self, params: BrowserTypeParams) -> ToolReturnValue:
        """Type text into an element."""
        return await self._call_mcp_tool(
            "browser_type",
            {
                "element": params.element,
                "ref": params.ref,
                "text": params.text,
                "submit": params.submit,
                "slowly": params.slowly,
            },
        )

    async def screenshot(self, params: BrowserScreenshotParams) -> ToolReturnValue:
        """Take a screenshot."""
        call_params: dict[str, Any] = {}
        if params.filename:
            call_params["filename"] = params.filename
        if params.fullPage:
            call_params["fullPage"] = params.fullPage
        if params.element and params.ref:
            call_params["element"] = params.element
            call_params["ref"] = params.ref

        return await self._call_mcp_tool("browser_screenshot", call_params)

    async def cleanup(self):
        """Cleanup browser resources."""
        if self._mcp_process:
            try:
                self._mcp_process.terminate()
                await asyncio.wait_for(
                    asyncio.to_thread(self._mcp_process.wait), timeout=5.0
                )
            except Exception:
                self._mcp_process.kill()
            finally:
                self._mcp_process = None
        self._mcp_client = None


# Create individual tool classes for each browser operation
class BrowserNavigate(CallableTool2[BrowserNavigateParams]):
    """Navigate to a URL in the browser."""

    name: str = "BrowserNavigate"
    description: str = load_desc(Path(__file__).parent / "browser.md", {})
    params: type[BrowserNavigateParams] = BrowserNavigateParams

    def __init__(self, runtime: Runtime):
        super().__init__()
        self._browser = BrowserTool(runtime)

    @override
    async def __call__(self, params: BrowserNavigateParams) -> ToolReturnValue:
        return await self._browser.navigate(params)


class BrowserSnapshot(CallableTool2[BrowserSnapshotParams]):
    """Get a snapshot of the current page."""

    name: str = "BrowserSnapshot"
    description: str = "Get an accessibility snapshot of the current browser page."
    params: type[BrowserSnapshotParams] = BrowserSnapshotParams

    def __init__(self, runtime: Runtime):
        super().__init__()
        self._browser = BrowserTool(runtime)

    @override
    async def __call__(self, params: BrowserSnapshotParams) -> ToolReturnValue:
        return await self._browser.snapshot(params)


class BrowserClick(CallableTool2[BrowserClickParams]):
    """Click on a page element."""

    name: str = "BrowserClick"
    description: str = "Click on an element in the browser page."
    params: type[BrowserClickParams] = BrowserClickParams

    def __init__(self, runtime: Runtime):
        super().__init__()
        self._browser = BrowserTool(runtime)

    @override
    async def __call__(self, params: BrowserClickParams) -> ToolReturnValue:
        return await self._browser.click(params)


class BrowserType(CallableTool2[BrowserTypeParams]):
    """Type text into a page element."""

    name: str = "BrowserType"
    description: str = "Type text into an editable element in the browser page."
    params: type[BrowserTypeParams] = BrowserTypeParams

    def __init__(self, runtime: Runtime):
        super().__init__()
        self._browser = BrowserTool(runtime)

    @override
    async def __call__(self, params: BrowserTypeParams) -> ToolReturnValue:
        return await self._browser.type_text(params)


class BrowserScreenshot(CallableTool2[BrowserScreenshotParams]):
    """Take a screenshot of the browser page."""

    name: str = "BrowserScreenshot"
    description: str = "Take a screenshot of the current browser page or a specific element."
    params: type[BrowserScreenshotParams] = BrowserScreenshotParams

    def __init__(self, runtime: Runtime):
        super().__init__()
        self._browser = BrowserTool(runtime)

    @override
    async def __call__(self, params: BrowserScreenshotParams) -> ToolReturnValue:
        return await self._browser.screenshot(params)

