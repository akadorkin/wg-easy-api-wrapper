# WG-Easy API Wrapper

A Command-Line Interface (CLI) tool for managing WireGuard clients via the WG-Easy API.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Create a Client](#create-a-client)
  - [Delete a Client](#delete-a-client)
  - [List Clients](#list-clients)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Create WireGuard Clients**: Easily add new clients to your WireGuard server.
- **Delete Clients**: Remove existing clients when they're no longer needed.
- **List Clients**: View all active clients with their details.
- **Automated Configuration**: Generates configuration files and QR codes for clients.

## Installation

### Prerequisites

- Python 3.7 or higher
- [WG-Easy](https://wg-easy.github.io/wg-easy/) server up and running
- Access credentials for the WG-Easy API

### Using `pip`

You can install the CLI tool using `pip`:

```bash
pip install wg-easy-api-wrapper
