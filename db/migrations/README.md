# Database Migrations Documentation

This README file provides information on how to handle database migrations for the Streamlit Invoice Application.

## Overview

Database migrations are essential for managing changes to the database schema over time. This application uses SQLite as its database, and migrations will help ensure that the database structure is consistent and up-to-date.

## Migration Process

1. **Creating a Migration**: 
   - When changes are made to the database schema (e.g., adding a new table or modifying an existing one), a new migration file should be created. This file will contain the SQL commands necessary to apply the changes.

2. **Applying Migrations**: 
   - To apply the migrations, execute the SQL commands in the migration file against the SQLite database. This can be done using a database management tool or through a script.

3. **Rolling Back Migrations**: 
   - If a migration needs to be undone, the corresponding SQL commands should be executed to revert the changes made by the migration.

## Best Practices

- Always back up the database before applying new migrations.
- Test migrations in a development environment before applying them to production.
- Keep migration files organized and well-documented to ensure clarity for future developers.

## Tools

Consider using migration tools or libraries that can automate the migration process, such as Alembic or Flask-Migrate, if the project scales in complexity.

## Conclusion

Proper management of database migrations is crucial for maintaining the integrity and performance of the Streamlit Invoice Application. Follow the outlined processes and best practices to ensure smooth updates to the database schema.