from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Todo


def todo_list(request):
    """
    Display all todos.
    """
    todos = Todo.objects.all()
    return render(request, 'todos/todo_list.html', {'todos': todos})


def todo_create(request):
    """
    Create a new todo item.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            Todo.objects.create(title=title)
            messages.success(request, 'Todo created successfully!')
            return redirect('todos:todo_list')
        else:
            messages.error(request, 'Title cannot be empty!')
    return render(request, 'todos/todo_form.html', {'form_title': 'Create Todo'})


def todo_update(request, pk):
    """
    Update an existing todo item.
    """
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        completed = request.POST.get('completed') == 'on'
        
        if title:
            todo.title = title
            todo.completed = completed
            todo.save()
            messages.success(request, 'Todo updated successfully!')
            return redirect('todos:todo_list')
        else:
            messages.error(request, 'Title cannot be empty!')
    
    return render(request, 'todos/todo_form.html', {
        'todo': todo,
        'form_title': 'Edit Todo'
    })


def todo_delete(request, pk):
    """
    Delete a todo item.
    """
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todos:todo_list')
    
    return render(request, 'todos/todo_confirm_delete.html', {'todo': todo})


def todo_toggle(request, pk):
    """
    Toggle the completed status of a todo.
    """
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    messages.success(request, f'Todo marked as {"completed" if todo.completed else "incomplete"}!')
    return redirect('todos:todo_list')
