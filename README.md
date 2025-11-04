# Streamlit Invoice App

## Overview
The Streamlit Invoice App is a bilingual multi-user platform designed for generating and managing invoices. It supports both English and Arabic languages, providing a seamless experience for users. The application features an authentication system, admin and agent dashboards, professional PDF output, and a modern user interface.

## Features
- **Bilingual Support**: Toggle between English and Arabic languages.
- **User Authentication**: Secure login for agents and admins.
- **Admin Dashboard**: Manage users, clients, and invoices.
- **Agent Dashboard**: Create and manage invoices.
- **PDF Generation**: Generate professional invoices in PDF format.
- **Modern UI Design**: Clean and responsive design for an optimal user experience.
- **SQLite Database**: Lightweight database for storing user and invoice data.
- **Error Handling**: Robust error handling to ensure smooth operation.
- **Performance Optimizations**: Efficient code and database queries for fast performance.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/streamlit-invoice-app.git
   ```
2. Navigate to the project directory:
   ```
   cd streamlit-invoice-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.
2. Run the Streamlit application:
   ```
   streamlit run app.py
   ```
3. Access the application in your web browser at `http://localhost:8501`.

## Database Setup
To set up the SQLite database, run the SQL schema defined in `db/schema.sql`. This will create the necessary tables for users, agents, clients, products, and invoices.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- Thanks to the Streamlit community for their support and resources.
- Special thanks to the contributors for their valuable input and improvements.