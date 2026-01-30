import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer(help="User Management CLI")

@cli.command(help="Drop all tables and recreate them with a default user")
def initialize():
    with get_session() as db:
        drop_all()
        create_db_and_tables()
        bob = User(username='bob', email='bob@mail.com', password='bobpass')
        db.add(bob)
        db.commit()
        db.refresh(bob)
        print("Database Initialized")

@cli.command(help="Get a single user by exact username")
def get_user(
    username: str = typer.Argument(..., help="Username to search for")
):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command(help="Get all users in the database")
def get_all_users():
    with get_session() as db:
        users = db.exec(select(User)).all()
        for user in users:
            print(user)

# ✅ Exercise 1
@cli.command(help="Search users by partial match of username OR email")
def search_user(
    query: str = typer.Argument(..., help="Partial username or email to search")
):
    with get_session() as db:
        users = db.exec(
            select(User).where(
                User.username.ilike(f"%{query}%") |
                User.email.ilike(f"%{query}%")
            )
        ).all()

        if not users:
            print("No matching users found.")
            return

        for user in users:
            print(user)

# ✅ Exercise 2
@cli.command(help="Get users using pagination (limit & offset)")
def get_users_paginated(
    limit: int = typer.Argument(10, help="Number of users to return"),
    offset: int = typer.Argument(0, help="Number of users to skip")
):
    with get_session() as db:
        users = db.exec(
            select(User).limit(limit).offset(offset)
        ).all()

        if not users:
            print("No users found for given range.")
            return

        for user in users:
            print(user)

@cli.command(help="Change a user's email address")
def change_email(
    username: str = typer.Argument(..., help="Username to update"),
    new_email: str = typer.Argument(..., help="New email address")
):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command(help="Create a new user")
def create_user(
    username: str = typer.Argument(..., help="New user's username"),
    email: str = typer.Argument(..., help="New user's email"),
    password: str = typer.Argument(..., help="New user's password")
):
    with get_session() as db:
        newuser = User(username=username, email=email, password=password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Username or email already taken!")
        else:
            print(newuser)

@cli.command(help="Delete a user by username")
def delete_user(
    username: str = typer.Argument(..., help="Username of user to delete")
):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

if __name__ == "__main__":
    cli()
