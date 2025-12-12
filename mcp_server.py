from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import sys
import os
import mysql.connector
import asyncio
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware

class StripUnknownArgumentsMiddleware(Middleware):
    """Middleware to strip unknown arguments from MCP feature invocations."""

    async def on_call_tool(self, context, call_next):
        """Filter out unknown arguments from tool calls."""
        try:
            # Only proceed if this is a tool call with non-zero arguments
            if context.fastmcp_context and context.message.arguments and len(context.message.arguments) > 0:
                tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
                tool_args = tool.parameters.get("properties", None)
                expected_args_names = set(tool_args.keys()) if tool_args else set()
                filtered_args = {k: v for k, v in context.message.arguments.items() if k in expected_args_names}
                unknown_args = set(context.message.arguments.keys()).difference(expected_args_names)
                context.message.arguments = filtered_args  # modify in place
        except Exception as e:  # pragma: no cover
            pass
        return await call_next(context)

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage application lifecycle with type-safe context"""
    conn = None

    try:
        # Connect using a loop.run_in_executor to avoid blocking
        def connect_db():
            return mysql.connector.connect(
                host=f"{os.environ.get("DB_SERVER")}",
                port=os.environ.get("DB_PORT"),
                user=f"{os.environ.get("MYSQL_USER")}",
                password=f"{os.environ.get("MYSQL_PASSWORD")}",
                database=f"{os.environ.get("MYSQL_DATABASE")}"
            )

        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(None, connect_db)

        # Yield a dictionary instead of a dataclass to match example
        yield {"conn": conn}
    except Exception as e:
        # Continue without database but with empty dict
        yield {"conn": None}

    finally:
        if conn:
            await asyncio.get_event_loop().run_in_executor(None, conn.close)

# Create an MCP server with the lifespan
mcp = FastMCP("Database", lifespan=app_lifespan)
mcp.add_middleware(StripUnknownArgumentsMiddleware())

@mcp.tool()
async def query_sql(ctx: Context, query: str = None) -> str:
    """
    Tool to query the SQL database with a custom query.
    
    Args:
        query: The SQL query to execute. If not provided, will run a default query.
    
    Returns:
        The query results as a string.
    """
    try:
        # Access the connection using dictionary access
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available. Check server logs for details."
        
        # Use default query if none provided
        if not query:
            query = "SHOW TABLES"
        
        # Execute query in a non-blocking way
        def run_query():
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                if cursor.description:  # Check if the query returns results
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return {"success": True, "results": results, "rowCount": len(results)}
                else:
                    # For non-SELECT queries (INSERT, UPDATE, etc.)
                    return {"success": True, "rowCount": cursor.rowcount, "message": f"Query affected {cursor.rowcount} rows"}
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                cursor.close()
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_query)
        
        if result["success"]:
            if "results" in result:
                return f"Query results: {result['results']}"
            else:
                return result["message"]
        else:
            return f"Query error: {result['error']}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def list_tables(ctx: Context) -> str:
    """List all tables in the database that can be queried."""
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def get_tables():
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
            
        loop = asyncio.get_event_loop()
        tables = await loop.run_in_executor(None, get_tables)
        
        return f"Available tables: {tables}"
    except Exception as e:
        return f"Error listing tables: {str(e)}"

@mcp.tool()
async def describe_table(ctx: Context, table_name: str) -> str:
    """
    Get the structure of a specific table.
    
    Args:
        table_name: Name of the table to describe
        
    Returns:
        Column information for the specified table
    """
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def get_structure():
            cursor = conn.cursor()
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = []
            for row in cursor.fetchall():
                col_name, data_type, max_length = row
                if max_length:
                    columns.append(f"{col_name} ({data_type}({max_length}))")
                else:
                    columns.append(f"{col_name} ({data_type})")
            cursor.close()
            return columns
            
        loop = asyncio.get_event_loop()
        structure = await loop.run_in_executor(None, get_structure)
        
        if structure:
            return f"Structure of table '{table_name}':\n" + "\n".join(structure)
        else:
            return f"Table '{table_name}' not found or has no columns."
    except Exception as e:
        return f"Error describing table: {str(e)}"

@mcp.tool()
async def execute_nonquery(ctx: Context, sql: str) -> str:
    """
    Execute a non-query SQL statement (INSERT, UPDATE, DELETE, etc.).
    
    Args:
        sql: The SQL statement to execute
        
    Returns:
        Result of the operation
    """
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def run_nonquery():
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                row_count = cursor.rowcount
                # Commit changes
                conn.commit()
                cursor.close()
                return {"success": True, "rowCount": row_count}
            except Exception as e:
                # Rollback in case of error
                conn.rollback()
                return {"success": False, "error": str(e)}
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_nonquery)
        
        if result["success"]:
            return f"Operation successful. Rows affected: {result['rowCount']}"
        else:
            return f"Operation failed: {result['error']}"
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

# Run the server

if __name__ == "__main__":
    load_dotenv()

    try:
        mcp.run(transport="http", host="0.0.0.0", port="8000")
    except Exception as e:
        sys.exit(1)