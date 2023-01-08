from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from .forms import MemoryForm
from .utils import get_user_social_info


def handler404(request, *args, **kwargs):
    response = render(request, 'error_404_template.html', context={
        "searched_path": request.path
    })
    response.status_code = 404
    return response


def get_welcome(request):
    return render(request, "welcome.html")


@login_required()
def list_memory(request):
    """
    Render 'list_memory.html'
    Context contains social_info of requested user and list of user's memories
    """
    return render(request, "list_memory.html", context={
        **get_user_social_info(request.user),
        "memories": [
            memory.memory_info() for memory in request.user.memory_set.all()
        ]
    }, status=200)


@login_required()
def create_memory(request):
    """
    Render 'create_memory.html'
    Context contain:
        social_info of requested user
        action = 'create'
        MemoryForm

    If request method is POST:
        validate submitted form and create new memory if successful
    """
    if request.method == "POST":
        form = MemoryForm(request.POST)

        if form.is_valid():
            new_memory = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"New memory #{new_memory.id} successfully created!"
            )

            return redirect("list_memory")

        messages.add_message(
            request,
            messages.ERROR,
            form.errors.as_json()
        )

    return render(request, "create_memory.html", context={
        **get_user_social_info(request.user),
        "action": "create",
        "form": MemoryForm(initial={
            "user": request.user.id,
        }),
    })


@login_required()
def edit_memory(request, memory_id):
    """
    Render 'create_memory.html'
    Context contain:
        social_info of requested user
        action = 'edit'
        MemoryForm with related memory as an instance

    Redirects to 'list_memory' if searched memory does not exist

    If request method is POST:
        validate submitted form and update memory if successful
    """
    memory = request.user.memory_set.filter(id=memory_id).first()

    if memory is None:
        messages.add_message(
            request,
            messages.ERROR,
            f"Memory #{memory_id} does not exist!"
        )

        return redirect("list_memory")

    if request.method == "POST":
        form = MemoryForm(request.POST, instance=memory)

        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Memory #{memory_id} successfully changed!"
            )

            return redirect("list_memory")

        messages.add_message(
            request,
            messages.ERROR,
            form.errors.as_json()
        )

    return render(request, "create_memory.html", context={
        **get_user_social_info(request.user),

        "memory_id": memory_id,
        "action": "edit",

        "form": MemoryForm(instance=memory),
    })


@login_required()
def delete_memory(request, memory_id):
    """
    Redirect user to 'list_memory' in any case

    If there is a memory for the passed id, deletes it
    """
    memory = request.user.memory_set.filter(id=memory_id).first()

    if memory is None:
        messages.add_message(
            request,
            messages.ERROR,
            f"Memory #{memory_id} does not exist!"
        )
    else:
        memory.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Memory #{memory_id} successfully deleted!"
        )

    return redirect("list_memory")
