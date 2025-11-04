# Streamlit Invoice System

## Overview
This project is a bilingual (English and Arabic) multi-user invoice management system built using Streamlit. It allows users to create, manage, and export invoices while providing a secure authentication system.

## Features
- **User Authentication**: Secure login system with roles for Admins and Agents.
- **Admin Dashboard**: Summary statistics, interactive charts, and invoice management.
- **Agent Dashboard**: Manage personal invoices, create new invoices, and update statuses.
- **PDF Generation**: Professional PDF output with support for Arabic text.
- **Bilingual Support**: Interface available in both English and Arabic.

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-invoice-app
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Run the SQL schema to create the necessary tables. You can execute the SQL commands in `db/schema.sql` using a SQLite client.

4. Configure environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage
- Access the application in your web browser at `http://localhost:8501`.
- Log in using the credentials for Admins or Agents.
- Navigate through the dashboard to manage invoices, clients, and products.

## Testing
- Run the tests located in the `tests` directory to ensure everything is functioning correctly.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For any inquiries, please contact [info@heomed.com](mailto:info@heomed.com).