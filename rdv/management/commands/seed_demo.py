from django.core.management.base import BaseCommand
from rdv.models import Hopital, Specialite, Medecin
class Command(BaseCommand):
    help = 'Ajoute des données de démonstration pour SamaRDV.'
    def handle(self,*args,**kwargs):
        data={
        'Cardiologie':['Hôpital Principal de Dakar','Hôpital Aristide Le Dantec'],
        'Pédiatrie':['Centre Hospitalier National de Pikine','Hôpital Principal de Dakar'],
        'Médecine générale':['Centre Hospitalier National de Pikine','Hôpital de Ziguinchor'],
        'Dermatologie':['Hôpital Aristide Le Dantec','Hôpital de Ziguinchor'],
        'Gynécologie':['Hôpital Principal de Dakar','Hôpital de Ziguinchor'],}
        specs={n:Specialite.objects.get_or_create(nom=n)[0] for n in data}
        hospdata=[('Hôpital Principal de Dakar','Dakar','Avenue Nelson Mandela','338392100','🏥'),('Hôpital Aristide Le Dantec','Dakar','Avenue Pasteur','338225050','🏨'),('Centre Hospitalier National de Pikine','Pikine','Pikine, Dakar','338345600','🏥'),('Hôpital de Ziguinchor','Ziguinchor','Centre-ville, Ziguinchor','339910000','🏩')]
        hs={}
        for nom,ville,adresse,tel,emoji in hospdata: hs[nom]=Hopital.objects.get_or_create(nom=nom,defaults={'ville':ville,'adresse':adresse,'tel':tel,'emoji':emoji,'rating':4.6})[0]
        for s,hopnoms in data.items():
            for hn in hopnoms: hs[hn].specialites.add(specs[s])
        doctors=[('Dr Aïssatou Ndiaye','Cardiologie','Hôpital Principal de Dakar',12),('Dr Mamadou Fall','Pédiatrie','Centre Hospitalier National de Pikine',8),('Dr Fatou Sarr','Médecine générale','Hôpital de Ziguinchor',10),('Dr Ibrahima Diop','Dermatologie','Hôpital Aristide Le Dantec',7),('Dr Aminata Ba','Gynécologie','Hôpital Principal de Dakar',9),('Dr Ousmane Diallo','Cardiologie','Hôpital Aristide Le Dantec',11),('Dr Mariama Camara','Pédiatrie','Hôpital de Ziguinchor',6)]
        for nom,s,hn,exp in doctors: Medecin.objects.get_or_create(nom=nom,hopital=hs[hn],specialite=specs[s],defaults={'experience':exp,'rating':4.7})
        self.stdout.write(self.style.SUCCESS('Données de démonstration SamaRDV ajoutées.'))
