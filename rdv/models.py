import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
class Utilisateur(AbstractUser):
    prenom = models.CharField('Prénom', max_length=80, blank=True)
    telephone = models.CharField('Téléphone', max_length=30, blank=True)
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    email = models.EmailField('Adresse e-mail', unique=True)
    REQUIRED_FIELDS = ['email']
    def __str__(self): return f'{self.prenom} {self.last_name}'.strip() or self.username
    class Meta: verbose_name='Utilisateur'; verbose_name_plural='Utilisateurs'
class Hopital(models.Model):
    nom=models.CharField('Nom',max_length=180); ville=models.CharField('Ville',max_length=100); adresse=models.CharField('Adresse',max_length=250,blank=True); tel=models.CharField('Téléphone',max_length=40,blank=True); emoji=models.CharField('Icône',max_length=12,default='🏥'); rating=models.DecimalField('Note',max_digits=3,decimal_places=1,default=4.5); specialites=models.ManyToManyField('Specialite',blank=True,related_name='hopitaux')
    def __str__(self): return self.nom
    class Meta: verbose_name='Hôpital'; verbose_name_plural='Hôpitaux'
class Specialite(models.Model):
    nom=models.CharField('Spécialité',max_length=100,unique=True)
    def __str__(self): return self.nom
    class Meta: verbose_name='Spécialité'; verbose_name_plural='Spécialités'
class Medecin(models.Model):
    nom=models.CharField('Nom du médecin',max_length=160); specialite=models.ForeignKey(Specialite,on_delete=models.PROTECT,related_name='medecins'); hopital=models.ForeignKey(Hopital,on_delete=models.CASCADE,related_name='medecins'); experience=models.PositiveSmallIntegerField('Années d’expérience',default=5); rating=models.DecimalField('Note',max_digits=3,decimal_places=1,default=4.7); actif=models.BooleanField('Actif',default=True)
    def __str__(self): return f'{self.nom} — {self.specialite}'
    class Meta: verbose_name='Médecin'; verbose_name_plural='Médecins'
def generer_reference():
    return uuid.uuid4().hex[:10].upper()

class RendezVous(models.Model):
    STATUTS=[('confirme','Confirmé'),('attente','En attente'),('annule','Annulé')]
    reference=models.CharField('Référence',max_length=12,unique=True,default=generer_reference); medecin=models.ForeignKey(Medecin,on_delete=models.PROTECT,related_name='rendez_vous'); utilisateur=models.ForeignKey(Utilisateur,on_delete=models.SET_NULL,null=True,blank=True,related_name='rendez_vous'); patient=models.CharField('Nom du patient',max_length=120); telephone=models.CharField('Téléphone',max_length=30); date=models.DateField('Date'); heure=models.TimeField('Heure'); motif=models.CharField('Motif',max_length=500,blank=True); statut=models.CharField('Statut',max_length=12,choices=STATUTS,default='confirme'); created_at=models.DateTimeField('Créé le',auto_now_add=True)
    def __str__(self): return f'{self.reference} — {self.patient} — {self.date}'
    class Meta:
        verbose_name='Rendez-vous'; verbose_name_plural='Rendez-vous'; ordering=['date','heure']; constraints=[models.UniqueConstraint(fields=['medecin','date','heure'],condition=~models.Q(statut='annule'),name='unique_rdv_medecin_date_heure_actif')]
class MessageContact(models.Model):
    nom=models.CharField(max_length=120); email=models.EmailField(); sujet=models.CharField(max_length=180); message=models.TextField(); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.sujet} — {self.email}'
    class Meta: verbose_name='Message de contact'; verbose_name_plural='Messages de contact'
