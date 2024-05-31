# SpaceSite_Fastapi

## Description

This is a demo website built with FastAPI. It uses JWT in cookies for authentication and a PostgreSQL database with SQLAlchemy and Alembic . Registered users can add an avatar and additional information. The application is containerized using Docker.

## Installation

Clone the repository

```bash
git git clone https://github.com/Ruslan-Bagautdinov/SpaceSite_Fastapi.git
```

Navigate to the directory

```bash
cd SpaceSite_Fastapi
```

Optional: Set the following environment variables in a `.env` file in the root directory for a custom database connection, a strong secret key, and custom token expiration limits. For random images on the home page, add your own Unsplash access key to the `.env` file.

```bash
# .env
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=<your-access-token-expire-minutes>
REFRESH_TOKEN_EXPIRE_MINUTES=<your-refresh-token-expire-minutes>
POSTGRES_HOST=<your-postgres-host>
POSTGRES_PORT=<your-postgres-port>
POSTGRES_DB=<your-postgres-database>
POSTGRES_USER=<your-postgres-user>
POSTGRES_PASSWORD=<your-postgres-password>
UNSPLASH_ACCESS_KEY=<your-unsplash-access-key>
```

Build and run the Docker containers

```bash
docker-compose up --build -d
```

Once composed, it takes time (half a minute to a minute) to wait for the database to initialize and perform further migrations and upgrades using Alembic, please be patient.

## Usage

Access the application

Open your web browser and navigate to http://localhost:8000.

## Contributing

We welcome contributions from the community. Please read our contributing guidelines before submitting a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

If you have any questions or need support, please contact us at ruslan3odey@gmail.com.
