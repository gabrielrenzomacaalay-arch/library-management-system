"""Create sample data in data/ (run once:  python seed_data.py).

Loans are dated relative to today so the overdue report has something to show.
"""
from datetime import date, timedelta

from main import DATA_DIR
from models import Library, Learner, Teacher, Storybook, Textbook, ReferenceMaterial
from services import LoanService
from storage import JsonRepository


def build_sample_library(today=None):
    today = today or date.today()
    lib = Library()
    for item in (
        Storybook("B001", "Ang Pagong at ang Matsing", "Jose Rizal", 3, "Grades 1-3"),
        Storybook("B002", "Si Juan Tamad", "Folk Tale", 2, "Grades 1-3", "Fair"),
        Storybook("B003", "Noli Me Tangere (Abridged)", "Jose Rizal", 4, "Grades 7-10"),
        Textbook("B004", "Science Grade 5", "DepEd", 5, "Science", 5),
        Textbook("B005", "Mathematics Grade 6", "DepEd", 5, "Mathematics", 6, "Good"),
        Textbook("B006", "Araling Panlipunan Grade 8", "DepEd", 3, "Social Studies", 8, "Poor"),
        ReferenceMaterial("B007", "Atlas of the Philippines", "NAMRIA", 1, "3rd Edition"),
        ReferenceMaterial("B008", "English Dictionary", "Merriam-Webster", 2, "11th Edition"),
    ):
        lib.add_item(item)
    for member in (
        Learner("M001", "Ana Reyes", 5, "Sampaguita"),
        Learner("M002", "Ben Santos", 6, "Narra"),
        Learner("M003", "Carla Dizon", 8, "Molave"),
        Teacher("M004", "Mrs. Lourdes Bonquin", "Science"),
    ):
        lib.add_member(member)

    svc = LoanService(lib, lambda: today)
    svc.borrow_item("M001", "B001", today - timedelta(days=10))   # 3 days overdue
    svc.borrow_item("M002", "B004", today - timedelta(days=2))
    svc.borrow_item("M004", "B003", today - timedelta(days=3))
    returned = svc.borrow_item("M003", "B002", today - timedelta(days=9))
    svc.return_item(returned.loan_id, today - timedelta(days=4))  # closed, history
    return lib


if __name__ == "__main__":
    JsonRepository(DATA_DIR).save_all(build_sample_library())
    print(f"Sample data written to {DATA_DIR}")
