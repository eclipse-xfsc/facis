"""
FACIS Simulation Service - Main Entry Point

Run with: python -m src.main
"""

import logging

import uvicorn

from src.api.rest.app import create_app

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the simulation service."""
    logger.info("Starting FACIS Simulation Service...")

    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
