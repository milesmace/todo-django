# Generated migration for TodoGroup and Todo.group field

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_default_group_for_existing_todos(apps, schema_editor):
    """Create a default group for any existing todos."""
    Todo = apps.get_model("todo", "Todo")
    TodoGroup = apps.get_model("todo", "TodoGroup")
    User = apps.get_model(settings.AUTH_USER_MODEL)

    # Get or create a default user (first superuser or first user)
    user = User.objects.first()
    if not user:
        # If no users exist, we can't create a group
        # Delete all todos instead
        Todo.objects.all().delete()
        return

    # Create a default group
    default_group, _ = TodoGroup.objects.get_or_create(
        name="Default Group",
        owner=user,
        defaults={"description": "Default group for existing todos"},
    )

    # Assign all existing todos to this group
    Todo.objects.filter(group__isnull=True).update(group=default_group)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("todo", "0002_todo_is_completed"),
    ]

    operations = [
        # Create TodoGroup model
        migrations.CreateModel(
            name="TodoGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="todo_groups",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Todo Group",
                "verbose_name_plural": "Todo Groups",
                "ordering": ["-created_at"],
            },
        ),
        # Add group field as nullable first
        migrations.AddField(
            model_name="todo",
            name="group",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to="todo.todogroup",
            ),
        ),
        # Create default group and assign existing todos
        migrations.RunPython(
            create_default_group_for_existing_todos,
            reverse_code=migrations.RunPython.noop,
        ),
        # Make group field non-nullable
        migrations.AlterField(
            model_name="todo",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to="todo.todogroup",
            ),
        ),
    ]
