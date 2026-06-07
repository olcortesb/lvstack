# lvstack

Local AWS services dashboard — visualize what's running on your AWS emulators.

📺 [Video demo](https://www.youtube.com/watch?v=HTfKjIMKjZc)

## What is this?

A dashboard to visualize services running on local AWS emulators. Supports 3 tools:

- **MiniStack** — 68 services
- **Floci** — 53 services
- **RobotoCore** — 157 services (46 native + 111 via moto)

Each one emulates AWS services on your machine — no account, no costs.

## Quick Start

```bash
git clone https://github.com/olcortesb/lvstack && cd lvstack
docker compose up -d
```

This starts 5 services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- MiniStack: port 4566
- Floci: port 4567
- RobotoCore: port 4569

Open `http://localhost:3000` to see the dashboard with all stacks and their services.

## Run a single emulator

```bash
# Only MiniStack
docker compose -f docker-compose.ministack.yml up -d

# Only Floci
docker compose -f docker-compose.floci.yml up -d

# Only RobotoCore
docker compose -f docker-compose.robotocore.yml up -d
```

The dashboard auto-detects which stacks are running (polls every 5s).

## Features

- Real-time service status with polling
- Official AWS service icons
- Filter by category (Compute, Storage, Database, Networking, etc.)
- Auto-detects online/offline stacks
- S3 bucket listing

## Tech Stack

- **Frontend**: Vue 3 + Vite + Tailwind CSS
- **Backend**: Python + FastAPI
- **Containers**: Docker Compose

## Project Structure

```
lvstack/
├── frontend/                      # Vue 3 app
├── backend/                       # FastAPI API
├── docker-compose.yml             # All services
├── docker-compose.ministack.yml   # MiniStack only
├── docker-compose.floci.yml       # Floci only
├── docker-compose.robotocore.yml  # RobotoCore only
└── LICENSE
```

## License

MIT
