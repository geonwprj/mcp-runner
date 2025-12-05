# main.py

from mcp.server.fastmcp import FastMCP
import tts_mcp.config as config
import tts_mcp.tools as tools

mcp = FastMCP("tts_mcp", host=config.HOST, port=config.PORT)

@mcp.tool()
def say(text: str) -> str:
    """Generate speech audio from raw text and return the public MinIO URL of the audio file."""
    config.logger.info("Received text: %s...", text[:20])
    return tools.say(text)

@mcp.tool()
def tts(url: str) -> str:
    """Generate speech audio from MinIO URL and return the public MinIO URL of the audio file."""
    config.logger.info("Received URL: %s", url)
    return tools.tts(url)

if __name__ == "__main__":
    try:
        # Runs the server
        mcp.run(transport=config.TRANSPORT)
    except KeyboardInterrupt:
        # Handles CTRL+C gracefully
        config.logger.info("\nServer stopped by user.")