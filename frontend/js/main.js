// ===== PAGE D'ACCUEIL =====

async function renderHopitaux() {
  const container = document.getElementById('hopitaux-featured');
  if (!container) return;
  try {
    const hopitaux = (await api('GET', '/hopitaux')).slice(0, 3);
    container.innerHTML = hopitaux.map((h) => `
      <div class="hopital-card" onclick="window.location='pages/hopitaux.html?q=${encodeURIComponent(h.nom)}'">
        <div class="hopital-header">
          <div class="hopital-logo">${esc(h.emoji)}</div>
          <div class="hopital-info">
            <h3>${esc(h.nom)}</h3>
            <span>📍 ${esc(h.ville)}</span>
          </div>
        </div>
        <div class="hopital-specialites">
          ${h.specialites.map((s) => `<span class="tag">${esc(s)}</span>`).join('')}
        </div>
        <div class="hopital-footer">
          <span class="rating">★ ${esc(h.rating)}</span>
          <span class="dispo">● ${esc(h.dispo)} créneaux libres (7 jours)</span>
        </div>
      </div>`).join('');
  } catch (e) {
    container.innerHTML = `<p class="form-erreur">${esc(e.message)}</p>`;
  }
}

// Compteurs animés : alimentés par /api/stats (chiffres réels de la base)
function animateCounters() {
  document.querySelectorAll('.stat-num').forEach((counter) => {
    const target = parseInt(counter.getAttribute('data-target'), 10) || 0;
    const step = Math.max(target / (1800 / 16), 0.1);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) { current = target; clearInterval(timer); }
      counter.textContent = Math.floor(current).toLocaleString('fr-FR');
    }, 16);
  });
}

async function initStats() {
  const section = document.querySelector('.stats');
  if (!section) return;
  try {
    const s = await api('GET', '/stats');
    const valeurs = { hopitaux: s.hopitaux, medecins: s.medecins, rendezVous: s.rendezVous, specialites: s.specialites };
    document.querySelectorAll('.stat-num').forEach((el) => { el.setAttribute('data-target', valeurs[el.dataset.stat] ?? 0); });
    const obs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) { animateCounters(); obs.disconnect(); }
    }, { threshold: 0.3 });
    obs.observe(section);
  } catch {
    document.querySelectorAll('.stat-num').forEach((el) => { el.textContent = '–'; });
  }
}

// Recherche : redirige vers la liste filtrée
function rechercherRDV(e) {
  e.preventDefault();
  const spec = document.getElementById('specialite')?.value;
  const q = document.getElementById('ville')?.value.trim();
  const date = document.getElementById('date-rdv')?.value;

  const params = new URLSearchParams();
  if (spec) params.set('spec', spec);
  if (q) params.set('q', q);
  if (date) params.set('date', date);
  window.location.href = 'pages/hopitaux.html' + (params.toString() ? '?' + params : '');
}

document.addEventListener('DOMContentLoaded', async () => {
  renderHopitaux();
  initStats();
  api('GET', '/specialites').then((v) => remplirSelect('specialite', v)).catch(() => {});

  const today = aujourdhui();
  document.querySelectorAll('input[type="date"]').forEach((d) => { d.min = today; d.value = today; });
});
