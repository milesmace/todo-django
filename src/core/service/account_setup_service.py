from todo.models import Todo, TodoGroup

from core.models import User


class AccountSetupService:
    @staticmethod
    def setup_account(user_id: int):
        user = User.objects.get(id=user_id)

        # Create default todo group for the user
        todo_group = TodoGroup.objects.create(
            name="Work 💼",
            owner=user,
        )

        # Create 3 sample todos for that todo group
        Todo.objects.create(
            title="Plan the next weeks schedule",
            group=todo_group,
        )
        Todo.objects.create(
            title="Connect with client regarding project",
            group=todo_group,
        )
        Todo.objects.create(
            title="Email the report of work log to the client",
            group=todo_group,
        )
