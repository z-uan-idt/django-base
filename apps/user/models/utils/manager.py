from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, fullname, password, is_superuser=False):
        if not username or not password or not fullname:
            raise ValueError("username, password and fullname are required")

        user = self.model(
            fullname=fullname,
            is_superuser=is_superuser,
            username=str(username).lower(),
        )
        user.set_password(password)
        user.save(using=self._db)

        if user.created_by is None:
            user.created_by = user
            user.save()

        return user

    def create_superuser(self, username, fullname, password):
        return self.create_user(
            username=username,
            password=password,
            fullname=fullname,
            is_superuser=True,
        )
