import click
from werkzeug.security import generate_password_hash

from ..api.common import ApiError
from ..extensions import db
from ..models import User
from ..services.validation import phone, password


def register_commands(app):
    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Add original bilingual demo courses without overwriting existing data."""
        from ..services.seed import seed_demo

        click.echo(f"Created {seed_demo()} demo courses. Existing data preserved.")

    def read_credentials():
        try:
            number = phone(click.prompt("Phone (+86)"))
            secret = password(
                {
                    "password": click.prompt(
                        "Password (8-128 characters)",
                        hide_input=True,
                        confirmation_prompt=True,
                    )
                }
            )
        except ApiError as error:
            raise click.ClickException(error.code)
        return number, secret

    @app.cli.command("create-admin")
    def create_admin():
        """Create a local administrator; no built-in or public default password."""
        number, secret = read_credentials()
        if db.session.scalar(db.select(User).where(User.phone == number)):
            raise click.ClickException(
                "Phone already exists. Existing roles are never changed."
            )
        db.session.add(
            User(
                phone=number,
                nickname="管理员",
                password_hash=generate_password_hash(secret),
                role="admin",
            )
        )
        db.session.commit()
        click.echo("Administrator created.")

    @app.cli.command("reset-password")
    def reset_password():
        """Reset an account password locally and revoke existing sessions."""
        number, secret = read_credentials()
        user = db.session.scalar(db.select(User).where(User.phone == number))
        if not user:
            raise click.ClickException("Account not found.")
        user.password_hash = generate_password_hash(secret)
        user.session_version += 1
        db.session.commit()
        click.echo("Password reset. Previous sessions revoked.")
