from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user_details.models import User
from .models import Page, PageSection, PageTemplate


class WebPagesTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpassword123',
            first_name='Staff',
            last_name='User',
            is_staff=True
        )
        
        # Create test template
        self.template = PageTemplate.objects.create(
            name='Test Template',
            description='A test template',
            html_structure='<div class="container">{{ content }}</div>'
        )
        
        # Create test page
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='This is a test page content.',
            template=self.template,
            status='published',
            author=self.user,
            meta_title='Test Page',
            meta_description='This is a test page',
            show_in_menu=True,
            menu_order=1
        )
        
        # Create test section
        self.section = PageSection.objects.create(
            page=self.page,
            name='Test Section',
            section_type='text',
            content='This is a test section content.',
            order=0
        )
        
        # Setup API client
        self.client = APIClient()
        # Setup Django test client for template views
        self.django_client = Client()

    def test_page_detail_view(self):
        """Test the page detail template view"""
        url = reverse('web_pages:page_detail', kwargs={'slug': self.page.slug})
        response = self.django_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_pages/page_detail.html')
        self.assertContains(response, 'Test Page')
        self.assertContains(response, 'This is a test page content.')
        self.assertContains(response, 'This is a test section content.')

    def test_homepage_view(self):
        """Test the homepage view"""
        # Set the test page as homepage
        self.page.is_homepage = True
        self.page.save()

        url = reverse('web_pages:homepage')
        response = self.django_client.get(url)
        # Should redirect to the page detail view
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('web_pages:page_detail', kwargs={'slug': self.page.slug}))

    def test_draft_page_not_visible_to_public(self):
        """Test that draft pages are not visible to non-staff users"""
        # Create a draft page
        draft_page = Page.objects.create(
            title='Draft Page',
            slug='draft-page',
            content='This is a draft page.',
            status='draft',
            author=self.user
        )

        url = reverse('web_pages:page_detail', kwargs={'slug': draft_page.slug})
        # Test with anonymous user
        response = self.django_client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test with staff user
        self.django_client.login(username='staffuser', password='staffpassword123')
        response = self.django_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Draft Page')

    def test_menu_pages_in_context(self):
        """Test that menu pages are included in the template context"""
        url = reverse('web_pages:page_detail', kwargs={'slug': self.page.slug})
        response = self.django_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('menu_pages', response.context)
        self.assertEqual(len(response.context['menu_pages']), 1)
        self.assertEqual(response.context['menu_pages'][0].title, 'Test Page')

    def test_list_pages_api(self):
        """Test retrieving a list of pages through API"""
        url = reverse('web_pages:api_pages-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Test Page')

    def test_retrieve_page_api(self):
        """Test retrieving a single page through API"""
        url = reverse('web_pages:api_pages-detail', kwargs={'slug': self.page.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Test Page')
        self.assertEqual(len(response.data['data']['sections']), 1)

    def test_create_page_authenticated(self):
        """Test creating a page when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('web_pages:pages-list')
        data = {
            'title': 'New Page',
            'content': 'This is a new page content.',
            'template': self.template.id,
            'status': 'draft',
            'meta_title': 'New Page',
            'meta_description': 'This is a new page',
            'show_in_menu': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Page.objects.count(), 2)
        self.assertEqual(Page.objects.get(slug='new-page').title, 'New Page')

    def test_create_page_unauthenticated(self):
        """Test creating a page when unauthenticated should fail"""
        url = reverse('web_pages:pages-list')
        data = {
            'title': 'New Page',
            'content': 'This is a new page content.',
            'template': self.template.id,
            'status': 'draft'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Page.objects.count(), 1)  # No new page created

    def test_update_page(self):
        """Test updating a page"""
        self.client.force_authenticate(user=self.user)
        url = reverse('web_pages:pages-detail', kwargs={'slug': self.page.slug})
        data = {
            'title': 'Updated Page',
            'content': 'This is updated content.',
            'status': 'published'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, 'Updated Page')
        self.assertEqual(self.page.content, 'This is updated content.')

    def test_delete_page(self):
        """Test deleting a page"""
        self.client.force_authenticate(user=self.user)
        url = reverse('web_pages:pages-detail', kwargs={'slug': self.page.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Page.objects.count(), 0)

    def test_list_templates(self):
        """Test retrieving a list of templates"""
        url = reverse('web_pages:templates-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Template')

    def test_list_sections(self):
        """Test retrieving a list of sections"""
        url = reverse('web_pages:sections-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Section')

    def test_filter_sections_by_page(self):
        """Test filtering sections by page"""
        url = f"{reverse('web_pages:sections-list')}?page={self.page.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Section')

    def test_create_section(self):
        """Test creating a section"""
        self.client.force_authenticate(user=self.user)
        url = reverse('web_pages:sections-list')
        data = {
            'page': self.page.id,
            'name': 'New Section',
            'section_type': 'html',
            'content': '<p>This is HTML content</p>',
            'order': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PageSection.objects.count(), 2)
        self.assertEqual(PageSection.objects.get(name='New Section').content, '<p>This is HTML content</p>')

    def test_reorder_sections(self):
        """Test reordering sections"""
        # Create another section
        section2 = PageSection.objects.create(
            page=self.page,
            name='Second Section',
            section_type='text',
            content='This is the second section.',
            order=1
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('web_pages:sections-reorder')
        data = {
            'page_id': self.page.id,
            'section_ids': [section2.id, self.section.id]  # Reverse the order
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if order was updated
        self.section.refresh_from_db()
        section2.refresh_from_db()
        self.assertEqual(self.section.order, 1)
        self.assertEqual(section2.order, 0)

    def test_homepage_endpoint(self):
        """Test the homepage endpoint"""
        # Set the test page as homepage
        self.page.is_homepage = True
        self.page.save()
        
        url = reverse('web_pages:pages-homepage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Test Page')
        self.assertTrue(response.data['data']['is_homepage'])

    def test_menu_endpoint(self):
        """Test the menu endpoint"""
        url = reverse('web_pages:pages-menu')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Test Page')
        self.assertTrue(response.data['data'][0]['show_in_menu'])