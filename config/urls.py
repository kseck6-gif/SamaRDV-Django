from django.contrib import admin
from django.urls import path, re_path
from django.http import FileResponse, Http404
from django.views.static import serve
from pathlib import Path
from rdv import views
FRONTEND = Path(__file__).resolve().parent.parent / 'frontend'
def frontend_file(request, path=''):
    target = (FRONTEND / path).resolve()
    if not str(target).startswith(str(FRONTEND.resolve())) or not target.is_file():
        target = FRONTEND / 'index.html'
    if not target.is_file(): raise Http404('Page introuvable')
    return FileResponse(open(target, 'rb'))
urlpatterns = [
 path('admin/', admin.site.urls),
 path('api/sante', views.sante),
 path('api/stats', views.stats), path('api/specialites', views.specialites), path('api/villes', views.villes),
 path('api/hopitaux', views.hopitaux), path('api/medecins', views.medecins), path('api/medecins/<int:medecin_id>/creneaux', views.creneaux),
 path('api/auth/inscription', views.inscription), path('api/auth/connexion', views.connexion), path('api/auth/moi', views.moi),
 path('api/rdv', views.rendez_vous), path('api/rdv/suivi', views.suivi_rdv), path('api/rdv/<str:reference>/annuler', views.annuler_rdv),
 path('api/contact', views.contact),
 re_path(r'^(?P<path>.*)$', frontend_file),
]
