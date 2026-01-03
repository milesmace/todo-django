from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend


class EmailLogBackend(BaseEmailBackend):
    pass


def test_mail():
    # This is a testing function
    print("Testing...")
