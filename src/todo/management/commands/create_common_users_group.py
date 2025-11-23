from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from todo.models import Todo, TodoGroup


class Command(BaseCommand):
    help = "Creates the 'Common Users' Django group and assigns permissions"

    def handle(self, *args, **options):
        group_name = "Common Users"
        group, created = Group.objects.get_or_create(name=group_name)

        # Get content types for Todo and TodoGroup models
        todo_content_type = ContentType.objects.get_for_model(Todo)
        todo_group_content_type = ContentType.objects.get_for_model(TodoGroup)

        # Get all permissions for Todo and TodoGroup
        todo_permissions = Permission.objects.filter(content_type=todo_content_type)
        todo_group_permissions = Permission.objects.filter(
            content_type=todo_group_content_type
        )

        # Assign permissions to the group
        group.permissions.add(*todo_permissions)
        group.permissions.add(*todo_group_permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created group "{group_name}" and assigned permissions'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Group "{group_name}" already exists. Permissions have been updated.'
                )
            )

        # Show assigned permissions
        permissions_count = group.permissions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Total permissions assigned to "{group_name}": {permissions_count}'
            )
        )
