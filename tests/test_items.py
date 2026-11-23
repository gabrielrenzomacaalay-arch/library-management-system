import unittest

from exceptions import ItemUnavailableError, InvalidReturnStateError
from models import (LibraryItem, Storybook, Textbook, ReferenceMaterial, item_from_dict)


class TestLibraryItems(unittest.TestCase):
    def test_valid_item_starts_fully_available(self):
        book = Storybook("B1", "Title", "Author", 3, "Grades 1-3")
        self.assertEqual((book.copies_owned, book.copies_available), (3, 3))

    def test_abstract_item_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            LibraryItem("B1", "T", "A", 1)

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            Storybook("B1", "   ", "Author", 1, "Grades 1-3")

    def test_negative_copies_rejected(self):
        with self.assertRaises(ValueError):
            Storybook("B1", "T", "A", -1, "Grades 1-3")

    def test_available_cannot_exceed_owned(self):
        with self.assertRaises(ValueError):
            Storybook("B1", "T", "A", 1, "Grades 1-3", copies_available=2)

    def test_invalid_condition_rejected(self):
        book = Storybook("B1", "T", "A", 1, "Grades 1-3")
        with self.assertRaises(ValueError):
            book.condition = "Shiny"

    def test_condition_is_normalised(self):
        book = Storybook("B1", "T", "A", 1, "Grades 1-3", condition="fair")
        self.assertEqual(book.condition, "Fair")

    def test_textbook_grade_bounds(self):
        with self.assertRaises(ValueError):
            Textbook("B1", "T", "A", 1, "Math", 13)
        self.assertEqual(Textbook("B1", "T", "A", 1, "Math", 12).grade_level, 12)

    def test_checkout_and_return_update_stock(self):
        book = Storybook("B1", "T", "A", 2, "Grades 1-3")
        book.checkout_copy()
        self.assertEqual(book.copies_available, 1)
        book.return_copy()
        self.assertEqual(book.copies_available, 2)

    def test_checkout_with_no_copies_raises_custom_error(self):
        book = Storybook("B1", "T", "A", 1, "Grades 1-3")
        book.checkout_copy()
        with self.assertRaises(ItemUnavailableError):
            book.checkout_copy()

    def test_cannot_return_more_copies_than_owned(self):
        book = Storybook("B1", "T", "A", 1, "Grades 1-3")
        with self.assertRaises(InvalidReturnStateError):
            book.return_copy()

    def test_write_off_reduces_owned_not_available(self):
        book = Storybook("B1", "T", "A", 2, "Grades 1-3")
        book.checkout_copy()
        book.write_off_copy()
        self.assertEqual((book.copies_owned, book.copies_available), (1, 1))

    def test_polymorphic_circulation_rules(self):
        items = [Storybook("B1", "T", "A", 1, "x"), Textbook("B2", "T", "A", 1, "x", 1),
                 ReferenceMaterial("B3", "T", "A", 1, "1st")]
        self.assertEqual([i.is_circulating() for i in items], [True, True, False])

    def test_serialisation_round_trip_preserves_subclass(self):
        original = Textbook("B2", "Science 5", "DepEd", 3, "Science", 5, "Poor", 2)
        clone = item_from_dict(original.to_dict())
        self.assertIsInstance(clone, Textbook)
        self.assertEqual(clone.to_dict(), original.to_dict())


if __name__ == "__main__":
    unittest.main()
