"""
Migration pour créer un utilisateur administrateur par défaut
"""
from django.contrib.auth import get_user_model
from django.db import migrations
from django.utils import timezone

User = get_user_model()


def create_default_admin(apps, schema_editor):
    """Crée un utilisateur administrateur par défaut si aucun n'existe"""
    
    # Vérifier si un utilisateur admin existe déjà
    if not User.objects.filter(username='admin').exists():
        # Créer l'utilisateur manuellement avec last_login défini
        # pour éviter l'erreur NOT NULL de PostgreSQL
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            date_joined=timezone.now(),
            last_login=timezone.now()
        )
        
        # Créer le profil utilisateur
        from GestionDepartement.models import UserProfile
        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.ADMIN,
            est_actif=True
        )
        print(f"Utilisateur administrateur créé: admin / admin123")
    else:
        print("L'utilisateur admin existe déjà")


def remove_default_admin(apps, schema_editor):
    """Supprime l'utilisateur administrateur par défaut (optionnel)"""
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDepartement', '0004_membre_departement_membre_est_responsable'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]

