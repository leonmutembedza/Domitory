# Domitory

A dormitory management system designed to simplify the administration of student housing, room assignments, resident records, and accommodation-related operations.

## Features

- Student registration and management
- Room allocation and tracking
- Dormitory occupancy monitoring
- Database-driven data storage
- Search and filtering capabilities
- Data import/export support
- Administrative reporting
- User-friendly interface

## Tech Stack

### Backend
- Python
- PostgreSQL

### Database
- Relational database schema
- Automated schema creation and management

### Tools & Libraries
- argparse
- pathlib
- logging
- psycopg2

## Project Structure

```text
Domitory/
│
├── src/
│   ├── database/
│       └── db.py
│       └── schema.py
│   ├── ingestion/
│       └── loader.py
│   ├── repository/
│   ├── reporting
│       └── queries.py
│   ├── reporting
│       └── serializer.py
│
├── data/
│   └── sample_data.*
│
├── exports/
│
├── main.py
├── requirements.txt
├── docker-compose.yaml
├── pyproject.toml
└── README.md
```

## Installation

### Clone the repository

```bash
git clone https://github.com/leonmutembedza/Domitory.git
cd Domitory
```

### Create a virtual environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py --students students.json --rooms rooms.json --host *Database Host* --user *Database User* --port *Database port* --password *Database Password* --database *Database Name*
```

The application will:

1. Create the database schema.
2. Load dormitory data.
3. Execute predefined queries.
4. Display results.
5. Export data when configured.

## Database Schema

The system manages information such as:

- Students
- Rooms
- Allocations
- Occupancy records

Relationships are enforced through foreign keys to maintain data integrity.

## Development

Create a new branch before making changes:

```bash
git checkout -b feature/my-feature
```

Commit changes:

```bash
git add .
git commit -m "Add new feature"
```

Push branch:

```bash
git push origin feature/my-feature
```

Then create a Pull Request to the `main` branch.

## Future Improvements

- Web dashboard
- Authentication and authorization
- Email notifications
- Room reservation system
- Analytics and reporting dashboard
- REST API integration

## Author

**Leon Mutembedza**

GitHub: https://github.com/leonmutembedza

## License

This project is licensed under the MIT License.
