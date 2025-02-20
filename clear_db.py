from website import create_app, db  # Import your Flask app and database
from website.models import User, Message, Room  # Import your models

app = create_app()  # Create an instance of your Flask app

def delete_all_records():
    with app.app_context():  # Ensure the Flask app is active
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())  # Delete all rows
        db.session.commit()
        print("All records deleted.")

delete_all_records()
