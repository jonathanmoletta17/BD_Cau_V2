# GLPI Data Service V3

Clean, simplified architecture with vertical slices for multi-context support (DTIC & SIS).

## Architecture

- **Core**: Shared configuration and database management
- **Modules**: Business contexts organized by vertical slices
  - `dtic/metadata`: Metadata management (Users, Groups, Entities, etc.)
  - `dtic/tickets`: Ticket management (core domain)
  - `sis/`: Future SIS context

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
uvicorn src.main:app --reload --port 8001

# Access docs
# http://localhost:8001/docs
```

## Testing

```bash
# Test core module
python test_core.py

# Test metadata module
python test_metadata.py

# Test tickets module
python test_tickets.py
```

## Project Structure

```
src/
├── core/               # Shared infrastructure
│   ├── config.py       # Configuration management
│   └── database.py     # Database session factory
│
└── modules/
    └── dtic/           # DTIC business context
        ├── metadata/   # Metadata vertical slice
        │   └── models.py
        └── tickets/    # Tickets vertical slice
            └── models.py
```

## Key Simplifications from V2

1. **No layered folders**: Everything for a feature is in one folder
2. **Models = Entities**: No separation between domain and database models
3. **Concrete classes**: No abstract interfaces unless truly needed
4. **Context isolation**: DTIC and SIS are completely separate

## Development

This is V3 - a clean rewrite maintaining 100% compatibility with the existing database schema while simplifying the codebase.
