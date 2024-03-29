from django.test import TestCase

from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='testpass'):
    """creates a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """test creating user with an email"""
        email = "test@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
                email=email,
                password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """to normalize and test the email entered"""
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "test123")
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """tests the user with invalid email argument"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_user_create_new_super_user(self):
        """test creating new super user"""
        user = get_user_model().objects.create_superuser(
                "test@gmail.com",
                "admin123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Student'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """test the ingredients tag representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="salt and pepper soup",
            time_minutes=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)
