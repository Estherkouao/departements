"""
Modèles Django pour la gestion des départements
Implémente toutes les commissions définies dans le cahier des charges
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Membre(models.Model):
    """Modèle représentant un membre/serviteur du département"""
    
    class Departement(models.TextChoices):
        ADA = 'ADA', 'ADA'
        ADN = 'ADN', 'ADN'
        CLASSE_BATEME = 'CLASSE_BATEME', 'Classe de Batême'
        COMMUNICATION = 'COMMUNICATION', 'Communication'
        ECODIM = 'ECODIM', 'ECODIM'
        EVANGELISATION = 'EVANGELISATION', 'Evangelisation'
        GESTION_CULTE = 'GESTION_CULTE', 'Gestion de Culte'
        LOGISTIQUE = 'LOGISTIQUE', 'Logistique'
        MUSIQUE_LOUANGE = 'MUSIQUE_LOUANGE', 'Musique et Louange'
        PORTIER = 'PORTIER', 'Portier'
        SAINTE_CENE = 'SAINTE_CENE', 'Sainte Cène'
    
    class Role(models.TextChoices):
        CHANTRE = 'CHANTRE', 'Chantre'
        MUSICIEN = 'MUSICIEN', 'Musicien'
        TECHNICIEN = 'TECHNICIEN', 'Technicien'
        ACCUEIL = 'ACCUEIL', 'Accueil'
        LOUEUR = 'LOUEUR', 'Loueur'
        SENTINELLE = 'SENTINELLE', 'Sentinelle'
        RESPONSABLE = 'RESPONSABLE', 'Responsable'
        MEMBRE = 'MEMBRE', 'Membre'
        STAGIAIRE = 'STAGIAIRE', 'Stagiaire'
    
    class Status(models.TextChoices):
        ACTIF = 'ACTIF', 'Actif'
        INACTIF = 'INACTIF', 'Inactif'
        EN_CONGE = 'EN_CONGE', 'En congé'
        SUSPENDU = 'SUSPENDU', 'Suspendu'
    
    # Informations personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    date_entree = models.DateField(default=timezone.now)
    
    # Rôle et statut
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBRE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIF)
    est_sentinelle = models.BooleanField(default=False)
    groupe_sentinelle = models.CharField(max_length=50, blank=True, default='', help_text="Groupe de sentinelle (A, B, C...)")
    
    # Département
    departement = models.CharField(
        max_length=30, 
        choices=Departement.choices, 
        blank=True,
        help_text="Département auquel le membre appartient"
    )
    est_responsable = models.BooleanField(
        default=False, 
        help_text="Cocher si ce membre est responsable d'un département"
    )
    
    # Santé spirituelle
    niveau_sante_spirituelle = models.IntegerField(
        default=75,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Note sur 100"
    )
    derniere_priere_collective = models.DateField(null=True, blank=True)
    observations_spirituelles = models.TextField(blank=True)
    
    # Informations bancaires (pour les soutiens)
    iban = models.CharField(max_length=50, blank=True)
    
    # Photo
    photo = models.ImageField(upload_to='membres/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom', 'prenom']
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Presence(models.Model):
    """Gestion des présences aux services et prières"""
    
    class TypeActivite(models.TextChoices):
        PRIERE_AVANT_1ER_CULTE = 'PRIERE_1', 'Prière avant 1er culte'
        PREMIER_CULTE = 'CULTE_1', '1er Culte'
        PRIERE_AVANT_2EME_CULTE = 'PRIERE_2', 'Prière avant 2ème culte'
        DEUXIEME_CULTE = 'CULTE_2', '2ème Culte'
        CULTE_BOSS = 'CULTE_BOSS', 'Culte des Boss'
        REVEIL_SENTINELLES = 'REVEIL_SENT', 'Réveil Sentinelles (Lundi 5h)'
        FORMATION = 'FORMATION', 'Formation'
        PRIERE_SENTINELLES = 'PRIERE_SENT', 'Prière des Sentinelles'
    
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    type_activite = models.CharField(max_length=20, choices=TypeActivite.choices)
    
    # Statut de présence
    EST_PRESENT = 'PRESENT'
    EST_ABSENT = 'ABSENT'
    EST_RETARD = 'RETARD'
    EST_EXCUSE = 'EXCUSE'
    
    class StatusPresence(models.TextChoices):
        PRESENT = 'PRESENT', 'Présent'
        ABSENT = 'ABSENT', 'Absent'
        RETARD = 'RETARD', 'En retard'
        EXCUSE = 'EXCUSE', 'Excusé'
    
    status = models.CharField(max_length=10, choices=StatusPresence.choices, default=StatusPresence.PRESENT)
    motif_absence = models.TextField(blank=True, help_text="Motif en cas d'absence")
    heure_arrivee = models.TimeField(null=True, blank=True, help_text="Heure d'arrivée pour les retards")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'type_activite']
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.get_type_activite_display()} - {self.date}"


class RapportCulte(models.Model):
    """Rapport de culte hebdomadaire"""
    
    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', 'Brouillon'
        SOUMIS = 'SOUMIS', 'Soumis'
        VALIDE = 'VALIDE', 'Validé'
    
    responsable = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, related_name='rapports_rediges')
    nom_departement = models.CharField(max_length=50, blank=True, help_text="Nom du département/Commission")
    date_culte = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.BROUILLON)
    
    # Nombres de serviteurs
    priere_1_nbre = models.IntegerField(default=0)
    priere_1_programme = models.IntegerField(default=0)
    priere_1_absent = models.IntegerField(default=0)
    priere_1_motifs = models.TextField(blank=True)
    
    culte_1_nbre = models.IntegerField(default=0)
    culte_1_programme = models.IntegerField(default=0)
    culte_1_absent = models.IntegerField(default=0)
    culte_1_motifs = models.TextField(blank=True)
    
    priere_2_nbre = models.IntegerField(default=0)
    priere_2_programme = models.IntegerField(default=0)
    priere_2_absent = models.IntegerField(default=0)
    priere_2_motifs = models.TextField(blank=True)
    
    culte_2_nbre = models.IntegerField(default=0)
    culte_2_programme = models.IntegerField(default=0)
    culte_2_absent = models.IntegerField(default=0)
    culte_2_motifs = models.TextField(blank=True)
    
    culte_boss_nbre = models.IntegerField(default=0)
    culte_boss_programme = models.IntegerField(default=0)
    culte_boss_absent = models.IntegerField(default=0)
    culte_boss_motifs = models.TextField(blank=True)
    
    reveil_sentinelles_nbre = models.IntegerField(default=0)
    reveil_sentinelles_programme = models.IntegerField(default=0)
    reveil_sentinelles_absent = models.IntegerField(default=0)
    reveil_sentinelles_motifs = models.TextField(blank=True)
    
    # Observations
    points_forts = models.TextField(blank=True)
    difficultes = models.TextField(blank=True)
    recommandations = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_culte']
        verbose_name = 'Rapport de culte'
        verbose_name_plural = 'Rapports de culte'
    
    def __str__(self):
        return f"Rapport du {self.date_culte}"


class TransmissionResume(models.Model):
    """Suivi de la transmission des résumés de culte"""
    
    class StatutTransmission(models.TextChoices):
        TRANSMIS = 'TRANSMIS', 'Transmis'
        NON_TRANSMIS = 'NON_TRANSMIS', 'Non transmis'
        EN_RETARD = 'EN_RETARD', 'En retard'
    
    serviteur = models.ForeignKey(Membre, on_delete=models.CASCADE)
    culte = models.CharField(max_length=50)  # 1er Culte, 2ème Culte, Culte des Boss
    date_culte = models.DateField()
    date_transmission = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=StatutTransmission.choices, default=StatutTransmission.NON_TRANSMIS)
    respect_delai = models.BooleanField(default=False)
    observation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_culte']
        verbose_name = 'Transmission de résumé'
        verbose_name_plural = 'Transmissions de résumés'
    
    def __str__(self):
        return f"{self.serviteur.nom_complet} - {self.culte} - {self.date_culte}"


class Stagiaire(models.Model):
    """Gestion des stagiaires"""
    
    class StatutStage(models.TextChoices):
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINE = 'TERMINE', 'Terminé'
        ABANDON = 'ABANDON', 'Abandonné'
        RECEVABLE = 'RECEVABLE', 'Recvable'
    
    # Informations personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    date_naissance = models.DateField()
    
    # Informations sur le stage
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    departement_accueil = models.CharField(max_length=100)
    taches_assignees = models.TextField()
    
    # Suivi
    tuteur = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name='stagiaires_encadres')
    statut = models.CharField(max_length=20, choices=StatutStage.choices, default=StatutStage.EN_COURS)
    
    # Évaluation
    evaluation_initiale = models.TextField(blank=True)
    evaluation_finale = models.TextField(blank=True)
    note_finale = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(20)])
    
    observations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Stagiaire'
        verbose_name_plural = 'Stagiaires'
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_statut_display()})"


class Evenement(models.Model):
    """Gestion des événements (communion, sorties, soutien)"""
    
    class TypeEvenement(models.TextChoices):
        AGAPE = 'AGAPE', 'Agape/Partage'
        VISITE = 'VISITE', 'Visite'
        SORTIE = 'SORTIE', 'Sortie/Activité'
        MARIAGE = 'MARIAGE', 'Mariage'
        DOT = 'DOT', 'Dot'
        ANNIVERSAIRE = 'ANNIVERSAIRE', 'Anniversaire'
        DECES = 'DECES', 'Déces'
        MALADIE = 'MALADIE', 'Maladie'
        NAISSANCE = 'NAISSANCE', 'Naissance/Accouchement'
        SOUTIEN = 'SOUTIEN', 'Soutien financier'
        AUTRE = 'AUTRE', 'Autre'
    
    type_evenement = models.CharField(max_length=20, choices=TypeEvenement.choices)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_evenement = models.DateField()
    lieu = models.CharField(max_length=200, blank=True)
    heure = models.TimeField(null=True, blank=True)
    
    # Participant(s) concerné(s)
    membres_concernes = models.ManyToManyField(Membre, related_name='evenements', blank=True)
    
    # Organisation
    responsable = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, related_name='evenements_organises')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Soutien financier
    montant_collecte = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_depense = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    # Statut
    EST_PREVU = 'PREVU'
    EST_REALISE = 'REALISE'
    EST_ANNULE = 'ANNULE'
    
    class StatutEvenement(models.TextChoices):
        PREVU = 'PREVU', 'Prévu'
        REALISE = 'REALISE', 'Réalisé'
        ANNULE = 'ANNULE', 'Annulé'
    
    statut = models.CharField(max_length=20, choices=StatutEvenement.choices, default=StatutEvenement.PREVU)
    
    class Meta:
        ordering = ['-date_evenement']
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
    
    def __str__(self):
        return f"{self.get_type_evenement_display()} - {self.titre}"


class Transaction(models.Model):
    """Gestion des transactions financières"""
    
    class TypeTransaction(models.TextChoices):
        COTISATION = 'COTISATION', 'Cotisation'
        COLLECTE = 'COLLECTE', 'Collecte'
        DON = 'DON', 'Don'
        DEPENSE = 'DEPENSE', 'Dépense'
        ACHAT = 'ACHAT', 'Achat'
        SOUTIEN = 'SOUTIEN', 'Soutien social'
        REMBOURSEMENT = 'REMBOURSEMENT', 'Remboursement'
    
    class TypeMouvement(models.TextChoices):
        ENTREE = 'ENTREE', 'Entrée'
        SORTIE = 'SORTIE', 'Sortie'
    
    type_transaction = models.CharField(max_length=20, choices=TypeTransaction.choices)
    type_mouvement = models.CharField(max_length=10, choices=TypeMouvement.choices)
    
    montant = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    
    description = models.TextField()
    date_transaction = models.DateField(default=timezone.now)
    
    # Provenance/Destination
    membre = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    departement = models.CharField(max_length=30, blank=True, help_text="Département concerné par la transaction")
    
    # Justification
    justification = models.TextField(blank=True)
    piece_justificative = models.FileField(upload_to='justificatifs/', null=True, blank=True)
    
    # Categorie
    class Categorie(models.TextChoices):
        LOGISTIQUE = 'LOGISTIQUE', 'Logistique'
        EQUIPEMENT = 'EQUIPEMENT', 'Équipement'
        FORMATION = 'FORMATION', 'Formation'
        COMMUNICATION = 'COMMUNICATION', 'Communication'
        SOCIAL = 'SOCIAL', 'Action sociale'
        CULTUREL = 'CULTUREL', 'Activité culturelle'
        AUTRE = 'AUTRE', 'Autre'
    
    categorie = models.CharField(max_length=20, choices=Categorie.choices, default=Categorie.AUTRE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_transaction']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.get_type_transaction_display()} - {self.montant} CFA - {self.date_transaction}"


class Impayes(models.Model):
    """Gestion des impayés - Suivi des cotisations non versées"""
    
    class StatutImpaye(models.TextChoices):
        EN_RETARD = 'EN_RETARD', 'En retard'
        RELANCE = 'RELANCE', 'Relancé'
        PAIE_PARTIEL = 'PAIE_PARTIEL', 'Payé partiellement'
        SOLDE = 'SOLDE', 'Soldé'
        ANNULE = 'ANNULE', 'Annulé'
    
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='impayes')
    type_cotisation = models.CharField(max_length=50, default='COTISATION', help_text="Type de cotisation")
    montant_du = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    montant_paye = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    periode_debut = models.DateField(help_text="Période de début (ex: mois/année)")
    periode_fin = models.DateField(null=True, blank=True, help_text="Période de fin")
    date_echeance = models.DateField(help_text="Date d'échéance")
    date_paiement = models.DateField(null=True, blank=True, help_text="Date du paiement")
    
    statut = models.CharField(max_length=20, choices=StatutImpaye.choices, default=StatutImpaye.EN_RETARD)
    
    # Relances
    nb_relances = models.IntegerField(default=0)
    date_derniere_relance = models.DateField(null=True, blank=True)
    observations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-periode_debut', '-date_echeance']
        verbose_name = 'Impayé'
        verbose_name_plural = 'Impayés'
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.montant_du} CFA - {self.get_statut_display()}"
    
    @property
    def montant_restant(self):
        return self.montant_du - self.montant_paye
    
    @property
    def est_en_retard(self):
        from django.utils import timezone
        return self.date_echeance < timezone.now().date() and self.statut not in [self.StatutImpaye.SOLDE, self.StatutImpaye.ANNULE]


class Budget(models.Model):
    """Gestion des budgets par catégorie"""
    
    class StatutBudget(models.TextChoices):
        PREVU = 'PREVU', 'Prévu'
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINER = 'TERMINER', 'Terminé'
        ANNULE = 'ANNULE', 'Annulé'
    
    annee = models.IntegerField(help_text="Année du budget")
    mois = models.IntegerField(null=True, blank=True, help_text="Mois du budget (optionnel pour budget mensuel)")
    
    # Catégorie
    class Categorie(models.TextChoices):
        LOGISTIQUE = 'LOGISTIQUE', 'Logistique'
        EQUIPEMENT = 'EQUIPEMENT', 'Équipement'
        FORMATION = 'FORMATION', 'Formation'
        COMMUNICATION = 'COMMUNICATION', 'Communication'
        SOCIAL = 'SOCIAL', 'Action sociale'
        CULTUREL = 'CULTUREL', 'Activité culturelle'
        AUTRE = 'AUTRE', 'Autre'
    
    categorie = models.CharField(max_length=20, choices=Categorie.choices)
    
    # Montants
    montant_prevu = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    montant_realise = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    # Statut
    statut = models.CharField(max_length=20, choices=StatutBudget.choices, default=StatutBudget.PREVU)
    
    # Justificatifs
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-annee', '-mois', 'categorie']
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        unique_together = ['annee', 'mois', 'categorie']
    
    def __str__(self):
        return f"Budget {self.get_categorie_display()} - {self.annee}"
    
    @property
    def taux_execution(self):
        if self.montant_prevu > 0:
            return (self.montant_realise / self.montant_prevu) * 100
        return 0
    
    @property
    def reste_budget(self):
        return self.montant_prevu - self.montant_realise


class FicheSanteSpirituelle(models.Model):
    """Fiche de santé spirituelle mensuelle des membres"""
    
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='fiches_sante')
    mois = models.DateField(help_text="Mois de la fiche")
    date_remplissage = models.DateTimeField(auto_now_add=True)
    
    # Questions spirituelles
    priere_quotidienne = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note de 1 à 5"
    )
    lecture_biblique = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communion_avec_dieu = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    assiduite_culte = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    service_rendu = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Score total (calculé)
    score_total = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    
    # Observations
    defis_spirituels = models.TextField(blank=True)
    objectifs_suivant_mois = models.TextField(blank=True)
    besoins_specifiques = models.TextField(blank=True)
    prieres = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-mois']
        verbose_name = 'Fiche de santé spirituelle'
        verbose_name_plural = 'Fiches de santé spirituelle'
        unique_together = ['membre', 'mois']
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.mois.strftime('%B %Y')}"
    
    def save(self, *args, **kwargs):
        # Calculer le score total automatiquement
        self.score_total = (
            self.priere_quotidienne +
            self.lecture_biblique +
            self.communion_avec_dieu +
            self.assiduite_culte +
            self.service_rendu
        )
        super().save(*args, **kwargs)


class GroupeService(models.Model):
    """Groupes de service et rotation"""
    
    nom_groupe = models.CharField(max_length=50)
    couleur = models.CharField(max_length=20, default='#FFD700', help_text="Couleur du groupe (hex)")
    description = models.TextField(blank=True)
    departement = models.CharField(max_length=30, blank=True, help_text="Département propriétaire du groupe")
    
    membres = models.ManyToManyField(Membre, related_name='groupes_service')
    
    # Jours de service
    jour_service = models.CharField(max_length=50, blank=True)  # Sunday, Saturday, etc.
    
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Groupe de service'
        verbose_name_plural = 'Groupes de service'
    
    def __str__(self):
        return self.nom_groupe


class PlanningService(models.Model):
    """Planning des services hebdomadaires"""
    
    date_service = models.DateField()
    type_service = models.CharField(max_length=50)  # 1er culte, 2eme culte, etc.
    
    groupe = models.ForeignKey(GroupeService, on_delete=models.CASCADE, related_name='plannings')
    
    # Tâches assignées
    assignations = models.JSONField(default=dict, help_text="{'louange': [membre_id], 'accueil': [membre_id], ...}")
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['date_service']
        verbose_name = 'Planning de service'
        verbose_name_plural = 'Plannings de service'
    
    def __str__(self):
        return f"{self.type_service} - {self.date_service}"


class Formation(models.Model):
    """Gestion des formations"""
    
    class StatutFormation(models.TextChoices):
        PLANIFIEE = 'PLANIFIEE', 'Planifiée'
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINEE = 'TERMINEE', 'Terminée'
        ANNULEE = 'ANNULEE', 'Annulée'
    
    class StatutValidation(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDEE = 'VALIDEE', 'Validée'
        REJETEE = 'REJETEE', 'Rejetée'
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    formateurs = models.ManyToManyField(Membre, related_name='formations_donnees')
    participants = models.ManyToManyField(Membre, related_name='formations_suivies', blank=True)
    
    lieu = models.CharField(max_length=200, blank=True)
    est_en_ligne = models.BooleanField(default=False)
    lien_online = models.URLField(blank=True)
    
    statut = models.CharField(max_length=20, choices=StatutFormation.choices, default=StatutFormation.PLANIFIEE)
    statut_validation = models.CharField(max_length=20, choices=StatutValidation.choices, default=StatutValidation.EN_ATTENTE)
    departement = models.CharField(max_length=50, blank=True, help_text="Département destinataire (vide = tous)")
    
    # Supports multimédias
    supports = models.FileField(upload_to='supports_formation/', null=True, blank=True, help_text="Document PDF")
    video = models.FileField(upload_to='formations/videos/', null=True, blank=True, help_text="Vidéo de formation")
    image = models.ImageField(upload_to='formations/images/', null=True, blank=True, help_text="Image/Affiche")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'
    
    def __str__(self):
        return self.titre


class Actualite(models.Model):
    """Actualités et communications"""
    
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='actualites/', null=True, blank=True)
    
    date_publication = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True)
    
    est_publie = models.BooleanField(default=True)
    est_urgent = models.BooleanField(default=False)
    
    # Catégorie
    class Categorie(models.TextChoices):
        CELEBRATION = 'CELEBRATION', 'Célébration'
        FORMATION = 'FORMATION', 'Formation'
        COMMUNION = 'COMMUNION', 'Communion'
        ANNONCE = 'ANNONCE', 'Annonce'
        AUTRE = 'AUTRE', 'Autre'
    
    categorie = models.CharField(max_length=20, choices=Categorie.choices, default=Categorie.AUTRE)
    
    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Actualité'
        verbose_name_plural = 'Actualités'
    
    def __str__(self):
        return self.titre


class MediaGalerie(models.Model):
    """Galerie de médias (photos et vidéos) pour documenter les moments forts"""
    
    class TypeMedia(models.TextChoices):
        IMAGE = 'image', 'Photo'
        VIDEO = 'video', 'Vidéo'
    
    titre = models.CharField(max_length=200)
    type_media = models.CharField(max_length=10, choices=TypeMedia.choices, default=TypeMedia.IMAGE)
    fichier = models.FileField(upload_to='galerie/', help_text="Photo ou vidéo")
    description = models.TextField(blank=True)
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    ajoute_par = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-date_ajout']
        verbose_name = 'Média galerie'
        verbose_name_plural = 'Médias galerie'
    
    def __str__(self):
        return f"{self.titre} ({self.get_type_media_display()})"


class Message(models.Model):
    """Messages et notifications internes"""
    
    class TypeMessage(models.TextChoices):
        INFORMATION = 'INFO', 'Information'
        ALERTE = 'ALERTE', 'Alerte'
        RAPPEL = 'RAPPEL', 'Rappel'
        URGENT = 'URGENT', 'Urgent'
    
    type_message = models.CharField(max_length=20, choices=TypeMessage.choices, default=TypeMessage.INFORMATION)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    
    date_envoi = models.DateTimeField(auto_now_add=True)
    expire_le = models.DateTimeField(null=True, blank=True)
    
    # Destinataires
    tous_les_membres = models.BooleanField(default=True)
    destinataires = models.ManyToManyField(Membre, related_name='messages_recus', blank=True)
    
    # Relais de communication
    relais = models.ManyToManyField(Membre, related_name='messages_relayes', blank=True)
    
    class Meta:
        ordering = ['-date_envoi']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.get_type_message_display()} - {self.titre}"


class Incident(models.Model):
    """Rapport d'incidents/discipline"""
    
    class TypeIncident(models.TextChoices):
        VERBAL = 'VERBAL', 'Avertissement verbal'
        ECRIT = 'ECRIT', 'Avertissement écrit'
        CONFLIT = 'CONFLIT', 'Conflit entre membres'
        COMPORTEMENT = 'COMPORTEMENT', 'Mauvais comportement'
        AUTRE = 'AUTRE', 'Autre'
    
    class StatutIncident(models.TextChoices):
        OUVERT = 'OUVERT', 'Ouvert'
        EN_COURS = 'EN_COURS', 'En cours'
        RESOLU = 'RESOLU', 'Résolu'
        CLOS = 'CLOS', 'Clos'
    
    type_incident = models.CharField(max_length=20, choices=TypeIncident.choices)
    statut = models.CharField(max_length=20, choices=StatutIncident.choices, default=StatutIncident.OUVERT)
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    
    membre_concerne = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='incidents')
    declare_par = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, related_name='incidents_declares')
    
    date_incident = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    resolution = models.TextField(blank=True)
    date_resolution = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_incident']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'
    
    def __str__(self):
        return f"{self.get_type_incident_display()} - {self.membre_concerne.nom_complet}"


class Commission(models.Model):
    """Modèle représentant les commissions du département"""
    
    class NomCommission(models.TextChoices):
        GESTION_RAPPORTS = 'GESTION_RAPPORTS', 'Gestion des Rapports'
        COMMUNION_INTEGRATION = 'COMMUNION_INTEGRATION', 'Communion Fraternelle + Intégration'
        FORMATION_TECHNIQUE = 'FORMATION_TECHNIQUE', 'Formation Technique'
        DISCIPLINE_SANTE = 'DISCIPLINE_SANTE', 'Discipline et Santé Spirituelle'
        TRESOR_FINANCE = 'TRESOR_FINANCE', 'Trésor, Finance et Gestion des Ressources'
        COMMUNICATION = 'COMMUNICATION', 'Communication'
        GESTION_SERVICE = 'GESTION_SERVICE', 'Gestion de Service (Rotation)'
    
    nom = models.CharField(max_length=50, choices=NomCommission.choices, unique=True)
    description = models.TextField(blank=True)
    
    # Responsable de la commission
    responsable = models.ForeignKey(
        Membre, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='commissions_dirigees'
    )
    
    # Membres de la commission
    membres = models.ManyToManyField(Membre, related_name='commissions', blank=True)
    
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom']
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'
    
    def __str__(self):
        return self.get_nom_display()


class Departement(models.Model):
    """Modèle représentant les départements de l'église avec responsables"""
    
    class NomDepartement(models.TextChoices):
        ADA = 'ADA', 'ADA'
        ADN = 'ADN', 'ADN'
        CLASSE_BATEME = 'CLASSE_BATEME', 'Classe de Batême'
        COMMUNICATION = 'COMMUNICATION', 'Communication'
        ECODIM = 'ECODIM', 'ECODIM'
        EVANGELISATION = 'EVANGELISATION', 'Evangelisation'
        GESTION_CULTE = 'GESTION_CULTE', 'Gestion de Culte'
        LOGISTIQUE = 'LOGISTIQUE', 'Logistique'
        MUSIQUE_LOUANGE = 'MUSIQUE_LOUANGE', 'Musique et Louange'
        PORTIER = 'PORTIER', 'Portier'
        SAINTE_CENE = 'SAINTE_CENE', 'Sainte Cène'
    
    nom = models.CharField(max_length=30, choices=NomDepartement.choices, unique=True)
    description = models.TextField(blank=True)
    
    # Responsable du département (membre)
    responsable = models.ForeignKey(
        Membre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departement_dirige'
    )
    
    # Compte utilisateur pour le responsable
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departement'
    )
    
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom']
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'
    
    def __str__(self):
        return self.get_nom_display()
    
    @property
    def a_responsable(self):
        """Vérifie si le département a un responsable avec compte"""
        return self.responsable is not None and self.user is not None


class UserProfile(models.Model):
    """Profil utilisateur étendu pour l'authentification"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        RESPONSABLE = 'RESPONSABLE', 'Responsable'
        TRESORIER = 'TRESORIER', 'Trésorier'
        SECRETAIRE = 'SECRETAIRE', 'Secrétaire'
        MEMBRE = 'MEMBRE', 'Membre'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    membre = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBRE)
    
    # Permissions
    peut_creer_rapport = models.BooleanField(default=True)
    peut_gerer_membres = models.BooleanField(default=False)
    peut_gerer_finances = models.BooleanField(default=False)
    peut_gerer_formations = models.BooleanField(default=False)
    peut_publier_actualites = models.BooleanField(default=False)
    peut_gerer_commissions = models.BooleanField(default=False)
    
    # Activité
    est_actif = models.BooleanField(default=True)
    date_derniere_connexion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Notification(models.Model):
    """Système de notifications"""
    
    class Type(models.TextChoices):
        INFO = 'INFO', 'Information'
        SUCCESS = 'SUCCESS', 'Succès'
        WARNING = 'WARNING', 'Avertissement'
        ERROR = 'ERROR', 'Erreur'
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True)
    
    est_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.titre} - {self.utilisateur.username}"


class ActiviteLog(models.Model):
    """Journal d'activité / Logs"""
    
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Créé'
        UPDATE = 'UPDATE', 'Modifié'
        DELETE = 'DELETE', 'Supprimé'
        LOGIN = 'LOGIN', 'Connexion'
        LOGOUT = 'LOGOUT', 'Déconnexion'
    
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activites')
    action = models.CharField(max_length=20, choices=Action.choices)
    modele = models.CharField(max_length=100)  # Ex: Membre, Transaction, etc.
    objet_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Log d\'activité'
        verbose_name_plural = 'Logs d\'activité'
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.action} - {self.modele} - {self.date_creation}"

