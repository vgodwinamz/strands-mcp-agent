import logging
from typing import List, Dict, Any, Optional
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strands-agent")

class StrandsAgent:
    """A simple wrapper around the Strands Agent with MCP tools"""
    
    def __init__(self, server_url: str = 'https://mcp-pg.agentic-ai-aws.com/sse', verbose: bool = False):
        """
        Initialize the Strands Agent with MCP tools
        
        Args:
            server_url: URL of the MCP server to connect to
            verbose: Whether to enable verbose logging
        """
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Connecting to MCP server: {server_url}")
        
        # Create MCP client
        self.mcp_client = MCPClient(lambda: sse_client(server_url))
        self.agent = None
        self.tools = []
        
    def __enter__(self):
        """Context manager entry"""
        self.mcp_client.__enter__()
        
        # Get the tools from the MCP server
        logger.info("Fetching available tools...")
        self.tools = self.mcp_client.list_tools_sync()
        
        # Create an agent with these tools
        logger.info("Creating agent with MCP tools")
        self.agent = Agent(tools=self.tools)
        
        # Display available tools
        logger.info(f"Available tools: {self.agent.tool_names}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.mcp_client.__exit__(exc_type, exc_val, exc_tb)
    
    def query(self, user_input: str) -> str:
        """
        Process a user query through the agent
        
        Args:
            user_input: The user's query
            
        Returns:
            The agent's response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use with context manager.")
        
        return self.agent(user_input)