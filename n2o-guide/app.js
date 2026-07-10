/* N2O Gewerbe-Guide – Wizard, Checkliste, Rechner. Alles lokal, kein Netzwerk. */
(function () {
  'use strict';
  var PREFIX = 'n2o-guide:';

  /* ---------- Persistenz: Checkboxen ---------- */
  var checkboxes = document.querySelectorAll('input[type="checkbox"][data-persist]');
  checkboxes.forEach(function (box) {
    box.checked = localStorage.getItem(PREFIX + box.id) === '1';
    box.addEventListener('change', function () {
      localStorage.setItem(PREFIX + box.id, box.checked ? '1' : '0');
      updateWizard();
      updateProgress();
    });
  });

  /* ---------- Persistenz: Zahlenfelder (Rechner) ---------- */
  var numFields = document.querySelectorAll('input[data-persist-val]');
  numFields.forEach(function (field) {
    var saved = localStorage.getItem(PREFIX + field.id);
    if (saved !== null) field.value = saved;
    field.addEventListener('input', function () {
      localStorage.setItem(PREFIX + field.id, field.value);
      updateCalc();
    });
  });

  /* ---------- Realitäts-Check ---------- */
  function updateWizard() {
    var gewerbe = document.getElementById('w-gewerbe').checked;
    var taetigkeit = document.getElementById('w-taetigkeit').checked;
    var lager = document.getElementById('w-lager').checked;
    var doku = document.getElementById('w-doku').checked;
    var box = document.getElementById('wizard-result');
    var count = [gewerbe, taetigkeit, lager, doku].filter(Boolean).length;

    box.className = 'status-box';
    if (count === 0) {
      box.classList.add('neutral');
      box.innerHTML = '<p>Noch nichts angekreuzt. Hake an, was real zutrifft – das Ergebnis erscheint hier.</p>';
    } else if (!taetigkeit) {
      box.classList.add('red');
      box.innerHTML = '<p><strong>⛔ Ohne reale Tätigkeit, die N₂O benötigt, ist gewerblicher Bezug keine Option.</strong> ' +
        'Ein Gewerbe, das nur zum Gasbezug angemeldet wird, ist eine Umgehung des NpSG – bei gewerbsmäßigem ' +
        'Inverkehrbringen drohen 1–10 Jahre Freiheitsstrafe, auch für Helfer. ' +
        'Siehe <a href="#recht">Rechtslage</a> und den Abschnitt für <a href="#privat">Privatpersonen</a>.</p>';
    } else if (count === 4) {
      box.classList.add('green');
      box.innerHTML = '<p><strong>✅ Grundvoraussetzungen für gewerblichen Bezug gegeben.</strong> ' +
        'Nächster Schritt: die <a href="#checkliste">Compliance-Checkliste</a> komplett durcharbeiten – ' +
        'erst dann lohnt die Lieferantenanfrage (<a href="#anbieter">Vorlage hier</a>).</p>';
    } else {
      var missing = [];
      if (!gewerbe) missing.push('Gewerbeanmeldung (Checkliste A1)');
      if (!lager) missing.push('geeigneter Lagerort (Checkliste B)');
      if (!doku) missing.push('Verwendungszweck-Dokumentation (Checkliste A3)');
      box.classList.add('amber');
      box.innerHTML = '<p><strong>🟡 Fast – es fehlt noch:</strong> ' + missing.join(', ') +
        '. Die reale Tätigkeit ist da, damit ist die Basis in Ordnung; die fehlenden Punkte ' +
        'führt die <a href="#checkliste">Checkliste</a> im Detail auf.</p>';
    }
  }

  /* ---------- Checklisten-Fortschritt ---------- */
  function updateProgress() {
    var all = document.querySelectorAll('input[data-cl]');
    var checkedTotal = 0;
    var groups = {};
    all.forEach(function (box) {
      var g = box.getAttribute('data-cl');
      groups[g] = groups[g] || { total: 0, done: 0 };
      groups[g].total++;
      if (box.checked) { groups[g].done++; checkedTotal++; }
    });
    Object.keys(groups).forEach(function (g) {
      var el = document.querySelector('[data-count="' + g + '"]');
      if (!el) return;
      el.textContent = '– ' + groups[g].done + ' / ' + groups[g].total + (groups[g].done === groups[g].total ? ' ✓' : '');
      el.classList.toggle('done', groups[g].done === groups[g].total);
    });
    var pct = all.length ? Math.round((checkedTotal / all.length) * 100) : 0;
    document.getElementById('progress-all').style.width = pct + '%';
    document.getElementById('progress-all-label').textContent = checkedTotal + ' / ' + all.length + ' (' + pct + ' %)';
  }

  /* ---------- Kostenrechner ---------- */
  function num(id) { return Math.max(0, parseFloat(document.getElementById(id).value) || 0); }
  function euro(v) {
    return v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 });
  }
  function updateCalc() {
    var bedarf = num('k-bedarf');
    var gas = bedarf * num('k-preis');
    var miete = num('k-flaschen') * num('k-miete') * 12;
    var liefer = num('k-liefer') * num('k-anzahl');
    var summe = gas + miete + liefer;
    document.getElementById('r-gas').textContent = euro(gas);
    document.getElementById('r-miete').textContent = euro(miete);
    document.getElementById('r-liefer').textContent = euro(liefer);
    document.getElementById('r-summe').textContent = euro(summe);
    document.getElementById('r-effektiv').textContent = bedarf > 0 ? euro(summe / bedarf) + ' / kg' : '–';
  }

  /* ---------- Buttons ---------- */
  document.getElementById('btn-print').addEventListener('click', function () {
    document.querySelectorAll('#checkliste details').forEach(function (d) { d.open = true; });
    window.print();
  });
  document.getElementById('btn-reset').addEventListener('click', function () {
    if (!confirm('Alle Haken und Eingaben zurücksetzen?')) return;
    Object.keys(localStorage)
      .filter(function (k) { return k.indexOf(PREFIX) === 0; })
      .forEach(function (k) { localStorage.removeItem(k); });
    location.reload();
  });
  document.getElementById('btn-copy').addEventListener('click', function () {
    var text = document.getElementById('mail-template').textContent;
    var btn = this;
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = 'Kopiert ✓';
      setTimeout(function () { btn.textContent = 'Kopieren'; }, 2000);
    }, function () {
      btn.textContent = 'Kopieren fehlgeschlagen';
    });
  });

  /* ---------- Init ---------- */
  updateWizard();
  updateProgress();
  updateCalc();
})();
