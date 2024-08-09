"""initial_migration

Revision ID: 429584cd5a51
Revises:
Create Date: 2024-08-09 17:10:16.173370

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User, UserProfile, Post


# revision identifiers, used by Alembic.
revision = '429584cd5a51'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the engine and session
    engine = op.get_bind()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the tables
    Base.metadata.create_all(engine)

    # Insert initial users and profiles with the provided hashed passwords
    hashed_password = "$2b$12$..LdVfFRwtPCdD.uIjFFS.CUqYIUCD1PaKl6liAFQcJ4Z1ZPI7A4C"
    user_user = User(username='user', hashed_password=hashed_password, email='user@example.com', role='user')
    user_admin = User(username='admin', hashed_password=hashed_password, email='admin@example.com', role='admin')

    session.add(user_user)
    session.add(user_admin)
    session.commit()

    user_profile_user = UserProfile(user_id=user_user.id)
    user_profile_admin = UserProfile(user_id=user_admin.id)

    session.add(user_profile_user)
    session.add(user_profile_admin)
    session.commit()


def downgrade():
    # Drop the tables
    Base.metadata.drop_all(op.get_bind())
