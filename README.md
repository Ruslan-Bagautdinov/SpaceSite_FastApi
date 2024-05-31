# SpaceSite_Fastapi

## Description

This is a demo website built with FastAPI. It uses JWT in cookies for authentication and a PostgreSQL database with SQLAlchemy and Alembic . Registered users can add an avatar and additional information. The application is containerized using Docker.

## Installation

1. **Clone the repository**
    ```
    git clone https://github.com/Ruslan-Bagautdinov/SpaceSite_Fastapi.git
    ```

2. **Navigate to the directory**
    ```
    cd SpaceSite_Fastapi
    ```

3. SECRET_KEY='<>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256

POSTGRES_HOST='localhost'
POSTGRES_PORT='5432'
POSTGRES_DB='fastapi_spacesite_pg'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='P0STGR3sql237996Qw!'

UNSPLASH_ACCESS_KEY='-_8j_P9TQ6fKmXnyk531pycsJCmy12s-roGAABWBkRg'

4. **Build and run the Docker containers**
    ```
    docker-compose up --build -d
    ```
Once composed, it takes time (half a minute to a minute) to wait for the database to initialize and perform further migrations and upgrades using Alembic, please be patient.

## Usage

1. **Access the application**
    - Open your web browser and navigate to `http://localhost:8000`.

## Contributing

We welcome contributions from the community. Please read our contributing guidelines before submitting a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

If you have any questions or need support, please contact us at ruslan3odey@gmail.com.
