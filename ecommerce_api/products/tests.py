from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from products.models import Product, Category, Order, OrderItem, Review
from products.serializers import ProductSerializer, CategorySerializer, OrderSerializer, ReviewSerializer

class CategoryViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('adminuser', 'admin@example.com', 'adminpassword')
        self.admin_token_response = self.client.post(reverse('api_token_auth'), {'username': 'adminuser', 'password': 'adminpassword'})
        self.admin_token = self.admin_token_response.data.get('token')
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')

    def test_category_list(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_category_retrieve(self):
        response = self.client.get(reverse('category-detail', args=[self.category1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_category_create_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'name': 'Books'}
        response = self.client.post(reverse('category-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

    def test_category_create_non_admin(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser', 'password': 'testpassword'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        data = {'name': 'Books'}
        response = self.client.post(reverse('category-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_update_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'name': 'Updated Electronics'}
        response = self.client.put(reverse('category-detail', args=[self.category1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(id=self.category1.id).name, 'Updated Electronics')

    def test_category_update_non_admin(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser', 'password': 'testpassword'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        data = {'name': 'Updated Electronics'}
        response = self.client.put(reverse('category-detail', args=[self.category1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_delete_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.delete(reverse('category-detail', args=[self.category1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)

    def test_category_delete_non_admin(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser', 'password': 'testpassword'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.delete(reverse('category-detail', args=[self.category1.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('adminuser', 'admin@example.com', 'adminpassword')
        self.admin_token_response = self.client.post(reverse('api_token_auth'), {'username': 'adminuser', 'password': 'adminpassword'})
        self.admin_token = self.admin_token_response.data.get('token')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser', 'password': 'testpassword'})
        self.user_token = self.user_token_response.data.get('token')
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')
        self.product1 = Product.objects.create(name='Laptop', description='Powerful laptop', price=1200.00, category=self.category1, stock_quantity=10, image_url='http://example.com/laptop.jpg')
        self.product2 = Product.objects.create(name='Smartphone', description='Latest smartphone', price=800.00, category=self.category1, stock_quantity=20, image_url='http://example.com/phone.jpg')

    def test_product_list_all(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 2) # Assuming pagination is enabled

    def test_product_retrieve_existing_id(self):
        response = self.client.get(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_product_retrieve_non_existing_id(self):
        response = self.client.get(reverse('product-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_create_valid_data_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'name': 'Tablet', 'description': 'Portable tablet', 'price': 300.00, 'category': self.category1.id, 'stock_quantity': 30, 'image_url': 'http://example.com/tablet.jpg'}
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_product_create_missing_required_fields_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'description': 'Portable tablet', 'category': self.category1.id} # Missing name, price, stock_quantity
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('price', response.data)
        self.assertIn('stock_quantity', response.data)

    def test_product_create_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        data = {'name': 'Tablet', 'description': 'Portable tablet', 'price': 300.00, 'category': self.category1.id, 'stock_quantity': 30, 'image_url': 'http://example.com/tablet.jpg'}
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_create_unauthenticated(self):
        data = {'name': 'Tablet', 'description': 'Portable tablet', 'price': 300.00, 'category': self.category1.id, 'stock_quantity': 30, 'image_url': 'http://example.com/tablet.jpg'}
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_update_valid_data_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'name': 'Updated Laptop', 'price': 1300.00, 'stock_quantity': 15} # Include stock_quantity
        response = self.client.put(reverse('product-detail', args=[self.product1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=self.product1.id).name, 'Updated Laptop')

    def test_product_update_invalid_data_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'price': 'invalid'}
        response = self.client.put(reverse('product-detail', args=[self.product1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_product_update_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        data = {'name': 'Updated Laptop', 'price': 1300.00}
        response = self.client.put(reverse('product-detail', args=[self.product1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_delete_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.delete(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)

    def test_product_delete_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        response = self.client.delete(reverse('product-detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('adminuser', 'admin@example.com', 'adminpassword')
        self.admin_token_response = self.client.post(reverse('api_token_auth'), {'username': 'adminuser', 'password': 'adminpassword'})
        self.admin_token = self.admin_token_response.data.get('token')
        self.user1 = User.objects.create_user('testuser1', 'test1@example.com', 'testpassword1')
        self.user2 = User.objects.create_user('testuser2', 'test2@example.com', 'testpassword2')

    def test_user_register_valid_data(self):
        data = {'username': 'newuser', 'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3) # Includes admin user

    def test_user_register_missing_required_fields(self):
        data = {'email': 'newuser@example.com', 'password': 'newpassword'} # Missing username
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_duplicate_username(self):
        data = {'username': 'testuser1', 'email': 'new@example.com', 'password': 'newpassword'}
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        data = {'username': 'testuser1', 'password': 'testpassword1'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_login_failure_invalid_credentials(self):
        data = {'username': 'testuser1', 'password': 'wrongpassword'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Or HTTP_401_UNAUTHORIZED

    def test_user_list_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2) # Excluding admin user in this count

    def test_user_list_non_admin(self):
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser1', 'password': 'testpassword1'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.user1.id)

    def test_user_retrieve_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.get(reverse('user-detail', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser1')

    def test_user_retrieve_non_admin_self(self):
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser1', 'password': 'testpassword1'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')