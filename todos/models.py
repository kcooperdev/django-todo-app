from django.db import models
from django.utils import timezone


class Todo(models.Model):
    """
    A model representing a todo item.
    """
    title = models.CharField(max_length=200, help_text="The text of the todo item")
    completed = models.BooleanField(default=False, help_text="Whether the todo is completed")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the todo was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the todo was last updated")
    
    class Meta:
        ordering = ['-created_at']  # Newest todos first
        verbose_name = "Todo"
        verbose_name_plural = "Todos"
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"
