from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# ── User Manager ──────────────────────────────────────────────────────────────
class UserManager(BaseUserManager):

    def create_user(self, phone, name, role='client', password=None):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, name=name, role=role)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password):
        user = self.create_user(phone=phone, name=name, role='admin', password=password)
        user.is_staff    = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ── User Model ────────────────────────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('admin',       'Admin'),
        ('client',      'Client'),
        ('contractor',  'Contractor'),
    ]

    # Core fields
    phone      = models.CharField(max_length=15, unique=True)
    name       = models.CharField(max_length=100)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    email      = models.EmailField(blank=True, null=True)

    # Status
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_users'
    )

    objects  = UserManager()

    USERNAME_FIELD  = 'phone'
    REQUIRED_FIELDS = ['name']

    class Meta:
        app_label = 'users'
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone}) — {self.role}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_contractor(self):
        return self.role == 'contractor'