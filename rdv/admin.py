from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Hopital, Specialite, Medecin, RendezVous, MessageContact
admin.site.site_header = 'SamaRDV — Administration'
admin.site.site_title = 'SamaRDV Admin'
admin.site.index_title = 'Gestion de la plateforme médicale'
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display=('username','email','prenom','last_name','telephone','is_staff','is_active')
    search_fields=('username','email','prenom','last_name','telephone')
    fieldsets=UserAdmin.fieldsets + (('Informations patient',{'fields':('prenom','telephone','date_naissance')}),)
    add_fieldsets=UserAdmin.add_fieldsets + (('Informations patient',{'fields':('email','prenom','telephone','date_naissance')}),)
@admin.register(Hopital)
class HopitalAdmin(admin.ModelAdmin):
    list_display=('nom','ville','tel','rating'); search_fields=('nom','ville'); list_filter=('ville','specialites'); filter_horizontal=('specialites',)
@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin): list_display=('nom',); search_fields=('nom',)
@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin): list_display=('nom','specialite','hopital','experience','rating','actif'); list_filter=('specialite','hopital','actif'); search_fields=('nom','hopital__nom')
@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin): list_display=('reference','patient','medecin','date','heure','statut','telephone'); list_filter=('statut','date','medecin__hopital','medecin__specialite'); search_fields=('reference','patient','telephone','medecin__nom'); date_hierarchy='date'; readonly_fields=('reference','created_at')
@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin): list_display=('sujet','nom','email','created_at'); search_fields=('nom','email','sujet'); readonly_fields=('created_at',)
