// ===== COUCHE D'ACCÈS À L'API (remplace l'ancien data.js / localStorage) =====
// Chargé sur toutes les pages avant les scripts propres à chaque page.

// Par défaut l'API est sur la même origine que le site (/api).
// Si le frontend est ouvert en file:// ou hébergé ailleurs, définir avant ce script :
//   <script>window.MEDIRDV_API_URL = 'https://mon-api.example';</script>
const API_BASE = (window.MEDIRDV_API_URL ?? (location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');

const CLE_TOKEN = 'samaRDV_token';
const CLE_USER = 'samaRDV_user';
const CLE_REFS = 'samaRDV_refs_invite';

// ---------- Session ----------
function lireJSON(cle, defaut) {
  try { return JSON.parse(localStorage.getItem(cle)) ?? defaut; } catch { return defaut; }
}
const getToken = () => localStorage.getItem(CLE_TOKEN);
const getUser = () => (getToken() ? lireJSON(CLE_USER, null) : null);

function setSession(token, utilisateur) {
  localStorage.setItem(CLE_TOKEN, token);
  localStorage.setItem(CLE_USER, JSON.stringify(utilisateur));
}

function deconnexion(e) {
  if (e) e.preventDefault();
  localStorage.removeItem(CLE_TOKEN);
  localStorage.removeItem(CLE_USER);
  // Les pages à données personnelles se rechargent ; les autres restent en place.
  window.location.reload();
}

// ---------- Rendez-vous pris sans compte : on garde les références ----------
const getRefsInvite = () => lireJSON(CLE_REFS, []);
function ajouterRefInvite(ref) {
  const refs = getRefsInvite();
  if (!refs.includes(ref)) localStorage.setItem(CLE_REFS, JSON.stringify([ref, ...refs].slice(0, 50)));
}

// ---------- Appels HTTP ----------
async function api(methode, chemin, corps) {
  const headers = {};
  if (corps !== undefined) headers['Content-Type'] = 'application/json';
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(API_BASE + '/api' + chemin, { method: methode, headers, body: corps !== undefined ? JSON.stringify(corps) : undefined });
  } catch {
    throw new Error("Impossible de joindre le serveur. Vérifiez votre connexion ou réessayez plus tard.");
  }

  let data = null;
  try { data = await res.json(); } catch { /* réponse sans corps JSON */ }

  if (!res.ok) {
    // Token expiré ou invalide : on nettoie la session pour éviter un état incohérent.
    if (res.status === 401 && token) { localStorage.removeItem(CLE_TOKEN); localStorage.removeItem(CLE_USER); }
    const err = new Error(data?.erreur || `Erreur ${res.status}`);
    err.statut = res.status;
    throw err;
  }
  return data;
}

// ---------- Utilitaires d'affichage ----------
// Toute donnée venant de l'API ou saisie par un utilisateur doit passer par esc() avant innerHTML.
function esc(valeur) {
  return String(valeur ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// Date du jour dans le fuseau du navigateur, au format AAAA-MM-JJ (toISOString donnerait la date UTC).
function aujourdhui() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// Une date AAAA-MM-JJ lue à midi évite le décalage d'un jour selon le fuseau.
const dateLocale = (iso) => new Date(`${iso}T12:00:00`);

function showToast(msg, duree = 3000) {
  document.querySelector('.toast')?.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), duree);
}

function toggleMenu() { document.body.classList.toggle('nav-open'); }

// Remplace les options d'un <select> par celles de l'API ; garde la 1re option (placeholder).
function remplirSelect(id, valeurs) {
  const sel = document.getElementById(id);
  if (!sel || !valeurs.length) return;
  const courant = sel.value;
  const placeholder = sel.options[0];
  sel.innerHTML = '';
  sel.appendChild(placeholder);
  valeurs.forEach((v) => { const o = document.createElement('option'); o.textContent = v; sel.appendChild(o); });
  sel.value = courant;
}

// Barre de navigation : affiche l'utilisateur connecté et le bouton Déconnexion.
function majNavigation() {
  const bouton = document.querySelector('.navbar .btn-nav');
  const user = getUser();
  if (!bouton || !user) return;
  const salut = document.createElement('span');
  salut.className = 'nav-user';
  salut.textContent = user.prenom ? `Bonjour, ${user.prenom}` : user.email;
  bouton.before(salut);
  bouton.textContent = 'Déconnexion';
  bouton.href = '#';
  bouton.addEventListener('click', deconnexion);
}

document.addEventListener('DOMContentLoaded', majNavigation);
