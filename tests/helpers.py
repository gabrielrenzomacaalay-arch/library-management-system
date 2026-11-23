"""Shared test fixtures."""
from datetime import date

from models import Library, Learner, Teacher, Storybook, Textbook, ReferenceMaterial
from services import LoanService

TODAY = date(2026, 11, 20)


def make_library():
    lib = Library()
    lib.add_item(Storybook("B001", "Ang Pagong at ang Matsing", "J. Rizal", 2, "Grades 1-3"))
    lib.add_item(Textbook("B002", "Science 5", "DepEd", 1, "Science", 5))
    lib.add_item(ReferenceMaterial("B003", "Atlas", "NAMRIA", 1, "3rd"))
    lib.add_item(Storybook("B004", "Si Juan Tamad", "Folk", 5, "Grades 1-3"))
    lib.add_member(Learner("M001", "Ana Reyes", 5, "Sampaguita"))
    lib.add_member(Teacher("M002", "Mrs. Cruz", "Science"))
    return lib


def make_service(lib=None):
    lib = lib or make_library()
    return lib, LoanService(lib, lambda: TODAY)
