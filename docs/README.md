# Documentation

Welcome to the standmate-be documentation! This folder contains all guides and setup instructions for the project.

## 📁 Folder Structure

```
docs/
├── setup/          # Setup and installation guides
│   ├── DOCKER_SETUP.md
│   └── PGADMIN_SETUP.md
└── guides/         # Development guides and references
    ├── MIGRATIONS_GUIDE.md
    └── SQLALCHEMY_GUIDE.md
```

## 🚀 Setup Guides

These guides help you set up your development environment:

### [Docker Setup](setup/DOCKER_SETUP.md)
Learn how to run PostgreSQL with Docker for local development.
- Docker installation
- Running PostgreSQL container
- Environment configuration
- Troubleshooting

### [pgAdmin Setup](setup/PGADMIN_SETUP.md)
Connect to your PostgreSQL database using pgAdmin for visual database management.
- Docker pgAdmin setup
- Desktop pgAdmin setup
- Connection configuration
- Viewing and querying data

## 📚 Development Guides

These guides help you work with the codebase:

### [Migrations Guide](guides/MIGRATIONS_GUIDE.md)
Complete guide to managing database schema changes using Alembic.
- What are migrations?
- Setting up Alembic
- Creating and applying migrations
- Common workflows
- Best practices
- Troubleshooting

### [SQLAlchemy Guide](guides/SQLALCHEMY_GUIDE.md)
Complete guide to using SQLAlchemy 2.0 with async support.
- Defining models
- CRUD operations
- Querying data
- Relationships
- Advanced queries
- Best practices

## 🎯 Quick Start

1. **Set up Docker and PostgreSQL:** [Docker Setup](setup/DOCKER_SETUP.md)
2. **Connect pgAdmin (optional):** [pgAdmin Setup](setup/PGADMIN_SETUP.md)
3. **Learn SQLAlchemy basics:** [SQLAlchemy Guide](guides/SQLALCHEMY_GUIDE.md)
4. **Manage database migrations:** [Migrations Guide](guides/MIGRATIONS_GUIDE.md)

## 📖 Additional Resources

- [Main README](../README.md) - Project overview and getting started
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

When adding new documentation:
- Place setup/installation guides in `setup/`
- Place development guides and references in `guides/`
- Use clear, descriptive filenames in UPPERCASE with underscores
- Update this README with links to new documents
