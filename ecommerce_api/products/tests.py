from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from products.models import Product, Category
from products.serializers import ProductSerializer

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
        data = {'name': 'Updated Laptop', 'price': 1300.00}
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

class UserTests(TestCase):
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
        self.assertEqual(len(response.data['results']), 2) # Excluding admin user in this count

    def test_user_list_non_admin(self):
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser1', 'password': 'testpassword1'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_retrieve_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.get(reverse('user-detail', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser1')

    def test_user_retrieve_non_admin_self(self):
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser1', 'password': 'testpassword1'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('user-detail', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser1')

    def test_user_retrieve_non_admin_other_user(self):
        user_token_response = self.client.post(reverse('api_token_auth'), {'username': 'testuser1', 'password': 'testpassword1'})
        user_token = user_token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('user-detail', args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        data = {'first_name': 'Updated', 'last_name': 'User'}
        response = self.client.put(reverse('user-detail', args=[self.user1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user1.id).first_name, 'Updated')

    def test_user_delete_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        response = self.client.delete(reverse('user-detail', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2) # Admin and one remaining user

class ProductSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')
        Product.objects.create(name='Laptop Pro', description='...', price=1500.00, category=self.category1, stock_quantity=5, image_url='...')
        Product.objects.create(name='Gaming Laptop', description='...', price=1800.00, category=self.category1, stock_quantity=8, image_url='...')
        Product.objects.create(name='T-Shirt', description='...', price=25.00, category=self.category2, stock_quantity=50, image_url='...')

    def test_product_search_by_name_partial_match(self):
        response = self.client.get(reverse('product-search') + '?q=laptop')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_product_search_by_category_partial_match(self):
        response = self.client.get(reverse('product-search') + '?q=electronic')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_product_search_no_results(self):
        response = self.client.get(reverse('product-search') + '?q=nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_product_search_pagination(self):
        Category.objects.create(name='Books')
        for i in range(15):
            Product.objects.create(name=f'Book {i}', description='...', price=10.00, category=Category.objects.get(name='Books'), stock_quantity=100, image_url='...')
        response_page1 = self.client.get(reverse('product-search') + '?q=book&page=1&page_size=5')
        self.assertEqual(response_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_page1.data['results']), 5)
        self.assertEqual(response_page1.data['count'], 15)
        self.assertIsNotNone(response_page1.data['next'])
        self.assertIsNone(response_page1.data['previous'])

        response_page3 = self.client.get(reverse('product-search') + '?q=book&page=3&page_size=5')
        self.assertEqual(response_page3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_page3.data['results']), 5)
        self.assertIsNotNone(response_page3.data['previous'])
        if response_page3.data['count'] > 15: # Handle potential extra products
            self.assertIsNotNone(response_page3.data['next'])
        else:
            self.assertIsNone(response_page3.data['next'])

class ProductFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')
        Product.objects.create(name='Laptop', description='...', price=1200.00, category=self.category1, stock_quantity=5, image_url='...')
        Product.objects.create(name='Smartphone', description='...', price=800.00, category=self.category1, stock_quantity=10, image_url='...')
        Product.objects.create(name='T-Shirt', description='...', price=25.00, category=self.category2, stock_quantity=50, image_url='...')
        Product.objects.create(name='Jeans', description='...', price=75.00, category=self.category2, stock_quantity=0, image_url='...')

    def test_product_filter_by_category(self):
        response = self.client.get(reverse('product-list') + f'?category={self.category1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        for product in response.data['results']:
            self.assertEqual(product['category'], self.category1.id)

    def test_product_filter_by_price_range(self):
        response_min_max = self.client.get(reverse('product-list') + '?price_min=50&price_max=1000')
        self.assertEqual(response_min_max.status_code, status.HTTP_200_OK)
        self.assertEqual(response_min_max.data['count'], 2)
        for product in response_min_max.data['results']:
            self.assertTrue(50 <= float(product['price']) <= 1000)

        response_min_only = self.client.get(reverse('product-list') + '?price_min=700')
        self.assertEqual(response_min_only.status_code, status.HTTP_200_OK)
        self.assertEqual(response_min_only.data['count'], 2)
        for product in response_min_only.data['results']:
            self.assertGreaterEqual(float(product['price']), 700)

        response_max_only = self.client.get(reverse('product-list') + '?price_max=100')
        self.assertEqual(response_max_only.status_code, status.HTTP_200_OK)
        self.assertEqual(response_max_only.data['count'], 1)
        for product in response_max_only.data['results']:
            self.assertLessEqual(float(product['price']), 100)

    def test_product_filter_by_stock_availability_true(self):
        response = self.client.get(reverse('product-list') + '?stock_available=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        for product in response.data['results']:
            self.assertGreater(product['stock_quantity'], 0)

    def test_product_filter_combine_filters(self):
        response = self.client.get(reverse('product-list') + f'?category={self.category2.id}&price_max=50&stock_available=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category'], self.category2.id)
        self.assertTrue(float(response.data['results'][0]['price']) <= 50)
        self.assertGreater(response.data['results'][0]['stock_quantity'], 0)

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user('authuser', 'auth@example.com', 'authpassword')

    def test_authentication_login_success(self):
        data = {'username': 'authuser', 'password': 'authpassword'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_authentication_login_failure_invalid_credentials(self):
        data = {'username': 'authuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Or 401 depending on settings

    def test_authentication_access_protected_without_token(self):
        response = self.client.post(reverse('product-list'), {'name': 'Test Product', 'price': 10.00, 'stock_quantity': 5, 'category': 1}) # Assuming category 1 exists
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_access_protected_with_token(self):
        user = User.objects.create_superuser('admin_auth', 'admin_auth@example.com', 'admin_auth_password')
        token_response = self.client.post(reverse('api_token_auth'), {'username': 'admin_auth', 'password': 'admin_auth_password'})
        token = token_response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        category = Category.objects.create(name='Test Category')
        data = {'name': 'Test Product', 'price': 10.00, 'stock_quantity': 5, 'category': category.id}
        response = self.client.post(reverse('product-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        