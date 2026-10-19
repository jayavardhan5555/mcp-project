"""MCP server exposing safe, read-only employee lookup tools."""
import json
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("employee-mcp")
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "employees.json"
mcp = FastMCP("Employee Directory")


def _load_employees() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Get non-sensitive directory details for one employee by numeric ID."""
    if not isinstance(employee_id, int) or isinstance(employee_id, bool) or employee_id <= 0:
        return {"ok": False, "error": "employee_id must be a positive integer"}
    employee = next((e for e in _load_employees() if e["employee_id"] == employee_id), None)
    if employee is None:
        logger.info("employee_lookup outcome=not_found")
        return {"ok": False, "error": "Employee not found"}
    logger.info("employee_lookup outcome=success")
    return {"ok": True, "employee": employee}


@mcp.tool()
def list_employees_by_department(department: str) -> dict:
    """List non-sensitive employee directory entries in a department."""
    if not isinstance(department, str) or not department.strip() or len(department) > 80:
        return {"ok": False, "error": "department must be a non-empty string of at most 80 characters"}
    matches = [e for e in _load_employees() if e["department"].casefold() == department.strip().casefold()]
    logger.info("department_lookup outcome=%s count=%d", "success", len(matches))
    return {"ok": True, "employees": matches}


if __name__ == "__main__":
    # Keep stdout reserved for the MCP stdio protocol.
    mcp.run(transport="stdio")
