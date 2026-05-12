from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra):
        if not username:
            raise ValueError('O username é obrigatório.')
        user = self.model(username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra.setdefault('perfil', 'ADMIN')
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    PERFIL_CHOICES = [
        ('ADMIN',       'Administrador'),
        ('FUNCIONARIO', 'Funcionário'),
    ]

    username  = models.CharField(max_length=50, unique=True)
    perfil    = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='FUNCIONARIO')
    ativo     = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table  = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.username} ({self.perfil})'

    @property
    def is_active(self):
        return self.ativo

    def is_admin(self):
        return self.perfil == 'ADMIN'
