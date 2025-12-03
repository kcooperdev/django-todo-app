from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import Todo


class TodoModelTest(TestCase):
    """Test cases for the Todo model."""
    
    def test_todo_creation(self):
        """Test creating a todo with valid data."""
        todo = Todo.objects.create(title="Test Todo")
        self.assertEqual(todo.title, "Test Todo")
        self.assertIsNotNone(todo.id)
    
    def test_todo_default_completed(self):
        """Test that new todos are not completed by default."""
        todo = Todo.objects.create(title="Test Todo")
        self.assertFalse(todo.completed)
    
    def test_todo_string_representation(self):
        """Test the string representation of a todo."""
        todo = Todo.objects.create(title="Test Todo")
        self.assertIn("Test Todo", str(todo))
        self.assertIn("○", str(todo))  # Incomplete symbol
        
        todo.completed = True
        todo.save()
        self.assertIn("✓", str(todo))  # Complete symbol
    
    def test_todo_ordering(self):
        """Test that todos are ordered by newest first."""
        todo1 = Todo.objects.create(title="First Todo")
        todo2 = Todo.objects.create(title="Second Todo")
        todo3 = Todo.objects.create(title="Third Todo")
        
        todos = list(Todo.objects.all())
        self.assertEqual(todos[0].title, "Third Todo")
        self.assertEqual(todos[1].title, "Second Todo")
        self.assertEqual(todos[2].title, "First Todo")


class TodoListViewTest(TestCase):
    """Test cases for the todo list view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('todos:todo_list')
    
    def test_list_view_with_todos(self):
        """Test list view displays todos."""
        Todo.objects.create(title="Todo 1")
        Todo.objects.create(title="Todo 2")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todo 1")
        self.assertContains(response, "Todo 2")
    
    def test_list_view_empty(self):
        """Test list view with no todos."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No todos yet!")


class TodoCreateViewTest(TestCase):
    """Test cases for the todo create view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('todos:todo_create')
    
    def test_create_view_get(self):
        """Test GET request shows create form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Todo")
    
    def test_create_todo_valid(self):
        """Test creating a todo with valid data."""
        response = self.client.post(self.url, {'title': 'New Todo'})
        
        # Should redirect to list view
        self.assertRedirects(response, reverse('todos:todo_list'))
        
        # Todo should be created
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
    
    def test_create_todo_empty_title(self):
        """Test creating a todo with empty title shows error."""
        response = self.client.post(self.url, {'title': ''})
        
        # Should not redirect (stays on form)
        self.assertEqual(response.status_code, 200)
        
        # Todo should not be created
        self.assertEqual(Todo.objects.count(), 0)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('cannot be empty', str(messages[0]))


class TodoUpdateViewTest(TestCase):
    """Test cases for the todo update view."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        self.todo = Todo.objects.create(title="Original Todo")
        self.url = reverse('todos:todo_update', args=[self.todo.pk])
    
    def test_update_view_get(self):
        """Test GET request shows update form with existing data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Todo")
        self.assertContains(response, "Original Todo")
    
    def test_update_todo_valid(self):
        """Test updating a todo with valid data."""
        response = self.client.post(self.url, {
            'title': 'Updated Todo',
            'completed': 'on'
        })
        
        # Should redirect to list view
        self.assertRedirects(response, reverse('todos:todo_list'))
        
        # Todo should be updated
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        self.assertTrue(self.todo.completed)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('updated successfully', str(messages[0]))
    
    def test_update_todo_empty_title(self):
        """Test updating a todo with empty title shows error."""
        response = self.client.post(self.url, {'title': ''})
        
        # Should not redirect (stays on form)
        self.assertEqual(response.status_code, 200)
        
        # Todo should not be updated
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Original Todo')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('cannot be empty', str(messages[0]))
    
    def test_update_nonexistent_todo(self):
        """Test updating a non-existent todo returns 404."""
        url = reverse('todos:todo_update', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoDeleteViewTest(TestCase):
    """Test cases for the todo delete view."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        self.todo = Todo.objects.create(title="Todo to Delete")
        self.url = reverse('todos:todo_delete', args=[self.todo.pk])
    
    def test_delete_view_get(self):
        """Test GET request shows delete confirmation."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure")
        self.assertContains(response, "Todo to Delete")
    
    def test_delete_todo(self):
        """Test deleting a todo."""
        response = self.client.post(self.url)
        
        # Should redirect to list view
        self.assertRedirects(response, reverse('todos:todo_list'))
        
        # Todo should be deleted
        self.assertFalse(Todo.objects.filter(pk=self.todo.pk).exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('deleted successfully', str(messages[0]))
    
    def test_delete_nonexistent_todo(self):
        """Test deleting a non-existent todo returns 404."""
        url = reverse('todos:todo_delete', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoToggleViewTest(TestCase):
    """Test cases for the todo toggle view."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        self.todo = Todo.objects.create(title="Test Todo", completed=False)
        self.url = reverse('todos:todo_toggle', args=[self.todo.pk])
    
    def test_toggle_incomplete_to_complete(self):
        """Test toggling an incomplete todo to complete."""
        self.assertFalse(self.todo.completed)
        
        response = self.client.get(self.url)
        
        # Should redirect to list view
        self.assertRedirects(response, reverse('todos:todo_list'))
        
        # Todo should be completed
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.completed)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('completed', str(messages[0]))
    
    def test_toggle_complete_to_incomplete(self):
        """Test toggling a complete todo to incomplete."""
        self.todo.completed = True
        self.todo.save()
        
        response = self.client.get(self.url)
        
        # Should redirect to list view
        self.assertRedirects(response, reverse('todos:todo_list'))
        
        # Todo should be incomplete
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.completed)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('incomplete', str(messages[0]))
    
    def test_toggle_nonexistent_todo(self):
        """Test toggling a non-existent todo returns 404."""
        url = reverse('todos:todo_toggle', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoURLTest(TestCase):
    """Test cases for URL routing."""
    
    def test_todo_list_url(self):
        """Test todo list URL resolves."""
        url = reverse('todos:todo_list')
        self.assertEqual(url, '/')
    
    def test_todo_create_url(self):
        """Test todo create URL resolves."""
        url = reverse('todos:todo_create')
        self.assertEqual(url, '/create/')
    
    def test_todo_update_url(self):
        """Test todo update URL resolves."""
        url = reverse('todos:todo_update', args=[1])
        self.assertEqual(url, '/1/update/')
    
    def test_todo_delete_url(self):
        """Test todo delete URL resolves."""
        url = reverse('todos:todo_delete', args=[1])
        self.assertEqual(url, '/1/delete/')
    
    def test_todo_toggle_url(self):
        """Test todo toggle URL resolves."""
        url = reverse('todos:todo_toggle', args=[1])
        self.assertEqual(url, '/1/toggle/')
