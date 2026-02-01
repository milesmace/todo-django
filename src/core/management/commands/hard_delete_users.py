from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from todo.models import Todo


class Command(BaseCommand):
    help = "Hard delete specified users along with their todo groups and todos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-ids",
            type=str,
            help="Comma-separated list of user IDs (e.g., '1,2,3')",
        )
        parser.add_argument(
            "--user-ids-range",
            type=str,
            help="Range of user IDs (e.g., '1-10')",
        )
        parser.add_argument(
            "--emails",
            type=str,
            help="Comma-separated list of user emails (e.g., 'user1@example.com,user2@example.com')",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        users_to_delete = []

        # Collect users based on provided arguments
        if options["user_ids"]:
            user_ids = [int(uid.strip()) for uid in options["user_ids"].split(",")]
            users = User.objects.filter(id__in=user_ids)
            users_to_delete.extend(users)

        if options["user_ids_range"]:
            range_parts = options["user_ids_range"].split("-")
            if len(range_parts) != 2:
                self.stdout.write(
                    self.style.ERROR(
                        "Invalid range format. Use 'start-end' (e.g., '1-10')"
                    )
                )
                return
            try:
                start_id = int(range_parts[0].strip())
                end_id = int(range_parts[1].strip())
                users = User.objects.filter(id__gte=start_id, id__lte=end_id)
                users_to_delete.extend(users)
            except ValueError:
                self.stdout.write(self.style.ERROR("Range values must be integers"))
                return

        if options["emails"]:
            email_list = [email.strip() for email in options["emails"].split(",")]
            users = User.objects.filter(email__in=email_list)
            users_to_delete.extend(users)

        # Remove duplicates while preserving order
        seen = set()
        unique_users = []
        for user in users_to_delete:
            if user.id not in seen:
                seen.add(user.id)
                unique_users.append(user)

        if not unique_users:
            self.stdout.write(
                self.style.WARNING(
                    "No users found to delete. Please provide --user-ids, --user-ids-range, or --emails"
                )
            )
            return

        # Confirm deletion
        self.stdout.write(
            self.style.WARNING(
                f"About to delete {len(unique_users)} user(s) along with their todo groups and todos:"
            )
        )
        for user in unique_users:
            todo_groups_count = user.todo_groups.count()
            todos_count = Todo.objects.filter(group__owner=user).count()
            self.stdout.write(
                f"  - User ID {user.id} ({user.email}): {todo_groups_count} todo group(s), {todos_count} todo(s)"
            )

        # Delete todos, todo groups, and users
        deleted_users_count = 0
        deleted_todo_groups_count = 0
        deleted_todos_count = 0

        for user in unique_users:
            # Get all todo groups for this user
            todo_groups = user.todo_groups.all()
            todo_groups_count = todo_groups.count()

            # Delete all todos in these todo groups
            for todo_group in todo_groups:
                todos = todo_group.todos.all()
                todos_count = todos.count()
                todos.delete()
                deleted_todos_count += todos_count

            # Delete all todo groups for this user
            todo_groups.delete()
            deleted_todo_groups_count += todo_groups_count

            # Finally, delete the user
            user.delete()
            deleted_users_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully deleted:\n"
                f"  - {deleted_users_count} user(s)\n"
                f"  - {deleted_todo_groups_count} todo group(s)\n"
                f"  - {deleted_todos_count} todo(s)"
            )
        )
