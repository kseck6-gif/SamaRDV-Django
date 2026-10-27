import json, uuid
from datetime import datetime, date, time, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import Hopital, Specialite, Medecin, RendezVous, MessageContact
User=get_user_model()
def body(request):
    try: return json.loads(request.body or b'{}')
    except (json.JSONDecodeError, UnicodeDecodeError): return {}
def error(message,status=400): return JsonResponse({'erreur':message},status=status)
def user_from_token(request):
    header=request.headers.get('Authorization','')
    if not header.startswith('Bearer '): return None
    try: return User.objects.filter(pk=AccessToken(header[7:])['user_id']).first()
    except Exception: return None
def public_user(u): return {'id':u.id,'prenom':u.prenom or u.first_name,'nom':u.last_name,'email':u.email,'telephone':u.telephone,'dateNaissance':u.date_naissance.isoformat() if u.date_naissance else ''}
def token_user(u): return {'token':str(RefreshToken.for_user(u).access_token),'utilisateur':public_user(u)}
def sante(request): return JsonResponse({'ok':True})
def stats(request): return JsonResponse({'hopitaux':Hopital.objects.count(),'medecins':Medecin.objects.filter(actif=True).count(),'specialites':Specialite.objects.count(),'rendezVous':RendezVous.objects.filter(statut='confirme').count()})
def specialites(request): return JsonResponse(list(Specialite.objects.values_list('nom',flat=True).order_by('nom')),safe=False)
def villes(request): return JsonResponse(list(Hopital.objects.values_list('ville',flat=True).distinct().order_by('ville')),safe=False)
def hopitaux(request):
    qs=Hopital.objects.prefetch_related('specialites').all()
    q=request.GET.get('q','').strip(); ville=request.GET.get('ville'); spec=request.GET.get('spec')
    if q: qs=qs.filter(nom__icontains=q) | qs.filter(ville__icontains=q)
    if ville: qs=qs.filter(ville=ville)
    if spec: qs=qs.filter(specialites__nom=spec)
    out=[]
    for h in qs.distinct().order_by('id'):
        out.append({'id':h.id,'nom':h.nom,'ville':h.ville,'emoji':h.emoji,'adresse':h.adresse,'tel':h.tel,'rating':float(h.rating),'specialites':list(h.specialites.values_list('nom',flat=True)),'dispo':sum(1 for r in range(14) if True)})
    return JsonResponse(out,safe=False)
def medecins(request):
    qs=Medecin.objects.filter(actif=True).select_related('specialite','hopital')
    spec=request.GET.get('spec'); ville=request.GET.get('ville'); q=request.GET.get('q','').strip(); hid=request.GET.get('hopitalId')
    if spec: qs=qs.filter(specialite__nom=spec)
    if ville: qs=qs.filter(hopital__ville=ville)
    if q: qs=qs.filter(nom__icontains=q) | qs.filter(hopital__nom__icontains=q) | qs.filter(hopital__ville__icontains=q)
    if hid:
        try: qs=qs.filter(hopital_id=int(hid))
        except ValueError: return error('Identifiant d’hôpital invalide.')
    return JsonResponse([{'id':m.id,'nom':m.nom,'specialite':m.specialite.nom,'experience':m.experience,'rating':float(m.rating),'hopitalId':m.hopital_id,'hopital':m.hopital.nom,'ville':m.hopital.ville} for m in qs.distinct()],safe=False)
def creneaux(request,medecin_id):
    if not Medecin.objects.filter(pk=medecin_id,actif=True).exists(): return error('Médecin introuvable.',404)
    try: d=date.fromisoformat(request.GET.get('date',''))
    except ValueError: return error('Date invalide (format AAAA-MM-JJ).')
    today=timezone.localdate()
    if d<today or d>today+timedelta(days=90): return error('Choisissez une date entre aujourd’hui et les 90 prochains jours.')
    reserved=set(RendezVous.objects.filter(medecin_id=medecin_id,date=d).exclude(statut='annule').values_list('heure',flat=True))
    slots=[]
    for hour in range(9,17):
        for minute in (0,30):
            t=time(hour,minute)
            if d==today and t<=timezone.localtime().time().replace(tzinfo=None): continue
            slots.append({'heure':t.strftime('%H:%M'),'disponible':t not in reserved})
    return JsonResponse({'medecinId':medecin_id,'date':d.isoformat(),'creneaux':slots})
@csrf_exempt
@require_http_methods(['POST'])
def inscription(request):
    b=body(request); prenom=str(b.get('prenom','')).strip(); nom=str(b.get('nom','')).strip(); email=str(b.get('email','')).strip().lower(); pwd=b.get('motDePasse','')
    if not prenom or not nom or not email or not pwd: return error('Veuillez remplir tous les champs obligatoires.')
    if len(pwd)<8: return error('Le mot de passe doit contenir au moins 8 caractères.')
    if User.objects.filter(email=email).exists(): return error('Un compte existe déjà avec cet email.',409)
    try:
        u=User.objects.create_user(username=email,email=email,password=pwd,first_name=prenom,last_name=nom,prenom=prenom,telephone=str(b.get('telephone','')))
        if b.get('dateNaissance'):
            try: u.date_naissance=date.fromisoformat(b['dateNaissance']); u.save(update_fields=['date_naissance'])
            except ValueError: pass
    except IntegrityError: return error('Un compte existe déjà avec cet email.',409)
    return JsonResponse(token_user(u),status=201)
@csrf_exempt
@require_http_methods(['POST'])
def connexion(request):
    b=body(request); email=str(b.get('email','')).strip().lower(); pwd=b.get('motDePasse','')
    u=authenticate(request,username=email,password=pwd)
    if not u: return error('Email ou mot de passe incorrect.',401)
    return JsonResponse(token_user(u))
def moi(request):
    u=user_from_token(request)
    if not u: return error('Authentification requise.',401)
    return JsonResponse({'utilisateur':public_user(u)})
def rdv_json(r): return {'reference':r.reference,'medecinId':r.medecin_id,'patient':r.patient,'tel':r.telephone,'date':r.date.isoformat(),'heure':r.heure.strftime('%H:%M'),'motif':r.motif,'statut':r.statut,'createdAt':r.created_at.isoformat(),'medecin':r.medecin.nom,'specialite':r.medecin.specialite.nom,'hopital':r.medecin.hopital.nom,'ville':r.medecin.hopital.ville}
@csrf_exempt
@require_http_methods(['GET','POST'])
def rendez_vous(request):
    if request.method=='GET':
        u=user_from_token(request)
        if not u: return error('Connectez-vous pour consulter vos rendez-vous.',401)
        return JsonResponse([rdv_json(r) for r in RendezVous.objects.filter(utilisateur=u).select_related('medecin__specialite','medecin__hopital')],safe=False)
    b=body(request)
    try: med_id=int(b.get('medecinId')); d=date.fromisoformat(b.get('date','')); t=time.fromisoformat(b.get('heure',''))
    except (TypeError,ValueError): return error('Médecin, date ou heure invalide.')
    patient=str(b.get('patient','')).strip(); tel=str(b.get('tel','')).strip(); motif=str(b.get('motif','')).strip()
    if len(patient)<2 or not tel: return error('Le nom du patient et le téléphone sont obligatoires.')
    if d<timezone.localdate(): return error('Cette date est déjà passée.')
    m=Medecin.objects.filter(pk=med_id,actif=True).select_related('specialite','hopital').first()
    if not m: return error('Médecin introuvable.',404)
    if t.minute not in (0,30) or t.hour<9 or t.hour>=17: return error('Ce médecin ne consulte pas à cette heure.')
    u=user_from_token(request); ref=uuid.uuid4().hex[:10].upper()
    try:
        with transaction.atomic(): r=RendezVous.objects.create(reference=ref,medecin=m,utilisateur=u,patient=patient,telephone=tel,date=d,heure=t,motif=motif,statut='confirme')
    except IntegrityError: return error('Ce créneau vient d’être réservé. Choisissez-en un autre.',409)
    return JsonResponse(rdv_json(r),status=201)
@csrf_exempt
@require_http_methods(['POST'])
def suivi_rdv(request):
    refs=body(request).get('references',[])
    if not isinstance(refs,list): refs=[]
    qs=RendezVous.objects.filter(reference__in=[str(x).replace('-','').upper() for x in refs[:50]]).select_related('medecin__specialite','medecin__hopital')
    return JsonResponse([rdv_json(r) for r in qs],safe=False)
@csrf_exempt
@require_http_methods(['PATCH'])
def annuler_rdv(request,reference):
    r=RendezVous.objects.filter(reference=reference.replace('-','').upper()).select_related('medecin__specialite','medecin__hopital').first()
    if not r: return error('Rendez-vous introuvable.',404)
    u=user_from_token(request)
    if r.utilisateur_id and (not u or r.utilisateur_id!=u.id): return error('Ce rendez-vous appartient à un autre compte.',403)
    if r.date<timezone.localdate(): return error('Un rendez-vous passé ne peut pas être annulé.')
    r.statut='annule'; r.save(update_fields=['statut']); return JsonResponse(rdv_json(r))
@csrf_exempt
@require_http_methods(['POST'])
def contact(request):
    b=body(request); nom=str(b.get('nom','')).strip(); email=str(b.get('email','')).strip(); sujet=str(b.get('sujet','')).strip(); message=str(b.get('message','')).strip()
    if not all([nom,email,sujet,message]): return error('Tous les champs sont obligatoires.')
    MessageContact.objects.create(nom=nom,email=email,sujet=sujet,message=message)
    return JsonResponse({'ok':True,'message':'Message envoyé.'},status=201)
