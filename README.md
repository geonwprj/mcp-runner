# MCP Runner

This repository contains the configuration and tooling to build and run Model Context Protocol (MCP) services using Docker and GitHub Actions.

## Overview

The project consists of:
- A generic **Docker image** (`mcp-runner`) that can install and run any Python-based MCP service at runtime.
- **GitHub Actions** to:
    - Publish individual Python services (like `tts_mcp`) to GitHub Packages.
    - Build and publish the Docker image to GitHub Container Registry (GHCR).

## Docker Usage

The Docker image is designed to be dynamic. It installs the requested service at runtime.

### Environment Variables

- `PYPI_URL`: **(Required)** The URL to the Python package (wheel or source) or the package name if available in the configured index.
- `PYPY_MODEL`: **(Optional)** The name of the module to run (e.g., `tts_mcp`). If not provided, the entrypoint attempts to guess it (but setting it is recommended).

### Example

```bash
docker run -e PYPI_URL="https://github.com/your-org/mcp-runner/releases/download/v0.1.0/tts_mcp-0.1.0-py3-none-any.whl" -e PYPY_MODEL="tts_mcp" ghcr.io/your-org/mcp-runner:latest
```

## GitHub Actions

### 1. Publish Library (`publish-library.yml`)
- **Trigger**: Manual (`workflow_dispatch`).
- **Purpose**: Builds a specific service (e.g., `tts_mcp`) and publishes the package to GitHub Packages.
- **Inputs**:
    - `service`: Select the service directory to build.

### 2. Publish Docker Image (`publish-docker.yml`)
- **Trigger**: Release (`published`).
- **Purpose**: Builds the `mcp-runner` Docker image and pushes it to GHCR.
- **Tags**: `latest` and the release version.

## Development

### Adding a New Service
1. Create a new directory for your service (e.g., `my_new_service`).
2. Add it to the `publish-library.yml` workflow inputs to enable building and publishing.
