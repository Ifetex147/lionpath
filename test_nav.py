from app import app
from navigation import get_directions

with app.app_context():
    print(get_directions("Computer Science Building",
                         "Faculty of Physical Sciences Library"))
    print()
    print(get_directions("Physics and Astronomy Building",
                         "Computer Science Building"))