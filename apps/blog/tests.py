from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user_details.models import User
from .models import BlogPost, BlogCategory, BlogTag, BlogComment


class BlogTests(TestCase):
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
        
        # Create test category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category'
        )
        
        # Create test tag
        self.tag = BlogTag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create test blog post
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            author=self.user,
            content='This is a test blog post content.',
            excerpt='Test excerpt',
            status='published'
        )
        self.blog_post.categories.add(self.category)
        self.blog_post.tags.add(self.tag)
        
        # Create test comment
        self.comment = BlogComment.objects.create(
            post=self.blog_post,
            author=self.user,
            content='This is a test comment',
            is_approved=True
        )
        
        # Setup API client
        self.client = APIClient()

    def test_list_blog_posts(self):
        """Test retrieving a list of blog posts"""
        url = reverse('blog:posts-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Test Blog Post')

    def test_retrieve_blog_post(self):
        """Test retrieving a single blog post"""
        url = reverse('blog:posts-detail', kwargs={'slug': self.blog_post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Test Blog Post')
        # Check that view count was incremented
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.views_count, 1)

    def test_create_blog_post_authenticated(self):
        """Test creating a blog post when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('blog:posts-list')
        data = {
            'title': 'New Blog Post',
            'content': 'This is a new blog post content.',
            'excerpt': 'New excerpt',
            'status': 'draft',
            'categories': [self.category.id],
            'tags': [self.tag.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 2)
        self.assertEqual(BlogPost.objects.get(slug='new-blog-post').title, 'New Blog Post')

    def test_create_blog_post_unauthenticated(self):
        """Test creating a blog post when unauthenticated should fail"""
        url = reverse('blog:posts-list')
        data = {
            'title': 'New Blog Post',
            'content': 'This is a new blog post content.',
            'excerpt': 'New excerpt',
            'status': 'draft'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(BlogPost.objects.count(), 1)  # No new post created

    def test_update_blog_post(self):
        """Test updating a blog post"""
        self.client.force_authenticate(user=self.user)
        url = reverse('blog:posts-detail', kwargs={'slug': self.blog_post.slug})
        data = {
            'title': 'Updated Blog Post',
            'content': 'This is updated content.',
            'excerpt': 'Updated excerpt',
            'status': 'published'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.title, 'Updated Blog Post')
        self.assertEqual(self.blog_post.content, 'This is updated content.')

    def test_delete_blog_post(self):
        """Test deleting a blog post"""
        self.client.force_authenticate(user=self.user)
        url = reverse('blog:posts-detail', kwargs={'slug': self.blog_post.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlogPost.objects.count(), 0)

    def test_list_categories(self):
        """Test retrieving a list of categories"""
        url = reverse('blog:categories-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Category')

    def test_list_tags(self):
        """Test retrieving a list of tags"""
        url = reverse('blog:tags-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Tag')

    def test_create_comment(self):
        """Test creating a comment"""
        self.client.force_authenticate(user=self.user)
        url = reverse('blog:comments-list')
        data = {
            'post': self.blog_post.id,
            'content': 'This is a new comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogComment.objects.count(), 2)
        # New comment should not be approved by default
        self.assertFalse(BlogComment.objects.get(content='This is a new comment').is_approved)

    def test_approve_comment(self):
        """Test approving a comment (staff only)"""
        # Create an unapproved comment
        unapproved_comment = BlogComment.objects.create(
            post=self.blog_post,
            author=self.user,
            content='This is an unapproved comment',
            is_approved=False
        )
        
        # Try to approve as regular user (should fail)
        self.client.force_authenticate(user=self.user)
        url = reverse('blog:comments-approve', kwargs={'pk': unapproved_comment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        unapproved_comment.refresh_from_db()
        self.assertFalse(unapproved_comment.is_approved)
        
        # Try to approve as staff user (should succeed)
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unapproved_comment.refresh_from_db()
        self.assertTrue(unapproved_comment.is_approved)