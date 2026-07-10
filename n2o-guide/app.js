/* N2O Gewerbe-Guide – geführter Modus, Checkliste, Generatoren, Verwaltung.
   Alles lokal (localStorage), kein Netzwerk. */
(function () {
  'use strict';
  var PREFIX = 'n2o-guide:';
  var STEP_COUNT = 9;

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function store(key, val) { localStorage.setItem(PREFIX + key, val); }
  function load(key) { return localStorage.getItem(PREFIX + key); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function euro(v) {
    return v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 });
  }
  function val(id) { var el = document.getElementById(id); return el ? el.value : ''; }
  function num(id) { return Math.max(0, parseFloat(val(id)) || 0); }

  /* ================= Theme ================= */
  var themeOrder = ['auto', 'light', 'dark'];
  function applyTheme(t) {
    if (t === 'auto') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', t);
    $('#theme-toggle').textContent = t === 'light' ? '☀️' : t === 'dark' ? '🌙' : '🌓';
  }
  var theme = load('theme') || 'auto';
  applyTheme(theme);
  $('#theme-toggle').addEventListener('click', function () {
    theme = themeOrder[(themeOrder.indexOf(theme) + 1) % themeOrder.length];
    store('theme', theme);
    applyTheme(theme);
  });

  /* ================= Modus (geführt / Handbuch) ================= */
  function setMode(mode) {
    document.body.classList.toggle('mode-guided', mode === 'guided');
    document.body.classList.toggle('mode-handbook', mode === 'handbook');
    $('#mode-guided-btn').classList.toggle('active', mode === 'guided');
    $('#mode-handbook-btn').classList.toggle('active', mode === 'handbook');
    store('mode', mode);
    if (mode === 'guided') showStep(currentStep);
  }
  $('#mode-guided-btn').addEventListener('click', function () { setMode('guided'); });
  $('#mode-handbook-btn').addEventListener('click', function () { setMode('handbook'); });

  /* ================= Schritt-Navigation ================= */
  var STEP_TITLES = ['', 'Realitäts-Check', 'Grundlagen', 'Qualität', 'Rechtslage',
    'Betriebsdaten', 'Compliance', 'Anbieter & Anfrage', 'Kosten', 'Verwaltung'];
  var currentStep = parseInt(load('step') || '1', 10);
  if (!(currentStep >= 1 && currentStep <= STEP_COUNT)) currentStep = 1;

  function showStep(n) {
    currentStep = Math.min(STEP_COUNT, Math.max(1, n));
    store('step', String(currentStep));
    $$('section.card').forEach(function (sec) {
      sec.classList.toggle('active-step', parseInt(sec.getAttribute('data-step'), 10) === currentStep);
    });
    $('#nav-status').textContent = 'Schritt ' + currentStep + ' / ' + STEP_COUNT + ' – ' + STEP_TITLES[currentStep];
    $('#nav-prev').disabled = currentStep === 1;
    $('#nav-next').textContent = currentStep === STEP_COUNT ? 'Fertig ✓' : 'Weiter →';
    updateRail();
    window.scrollTo({ top: 0 });
  }
  $('#nav-prev').addEventListener('click', function () { showStep(currentStep - 1); });
  $('#nav-next').addEventListener('click', function () {
    if (currentStep < STEP_COUNT) showStep(currentStep + 1);
    else setMode('handbook');
  });
  $$('#step-rail li').forEach(function (li) {
    li.addEventListener('click', function () { showStep(parseInt(li.getAttribute('data-goto'), 10)); });
  });

  /* ================= Persistenz ================= */
  $$('input[type="checkbox"][data-persist]').forEach(function (box) {
    box.checked = load(box.id) === '1';
    box.addEventListener('change', function () {
      store(box.id, box.checked ? '1' : '0');
      updateAll();
    });
  });
  $$('[data-persist-val]').forEach(function (field) {
    var saved = load(field.id);
    if (saved !== null) field.value = saved;
    ['input', 'change'].forEach(function (evt) {
      field.addEventListener(evt, function () {
        store(field.id, field.value);
        updateAll();
      });
    });
  });
  $$('input[type="radio"][data-persist-radio]').forEach(function (radio) {
    if (load('radio:' + radio.name) === radio.value) radio.checked = true;
    radio.addEventListener('change', function () {
      if (radio.checked) store('radio:' + radio.name, radio.value);
      updateAll();
    });
  });

  /* ================= Realitäts-Check ================= */
  function updateWizard() {
    var gewerbe = $('#w-gewerbe').checked;
    var taetigkeit = $('#w-taetigkeit').checked;
    var lager = $('#w-lager').checked;
    var doku = $('#w-doku').checked;
    var box = $('#wizard-result');
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
        'Weiter durch die Schritte: Wissen auffrischen, Qualität wählen, Betriebsdaten erfassen ' +
        'und die <a href="#checkliste">Compliance-Checkliste</a> komplett abarbeiten – erst dann lohnt die Anfrage.</p>';
    } else {
      var missing = [];
      if (!gewerbe) missing.push('Gewerbeanmeldung (Checkliste A1)');
      if (!lager) missing.push('geeigneter Lagerort (Checkliste B)');
      if (!doku) missing.push('Verwendungszweck-Doku (Generator in Schritt 5)');
      box.classList.add('amber');
      box.innerHTML = '<p><strong>🟡 Fast – es fehlt noch:</strong> ' + missing.join(', ') +
        '. Die reale Tätigkeit ist da, damit ist die Basis in Ordnung; der Rest wird in den nächsten Schritten erledigt.</p>';
    }
  }

  /* ================= Quiz ================= */
  function evalQuiz(silent) {
    var right = 0, answered = 0;
    var qs = $$('.quiz-q');
    qs.forEach(function (q) {
      var sel = q.querySelector('input:checked');
      q.classList.remove('correct', 'wrong');
      if (!sel) return;
      answered++;
      if (sel.value === q.getAttribute('data-correct')) { right++; q.classList.add('correct'); }
      else q.classList.add('wrong');
    });
    var box = $('#quiz-result');
    if (!silent) {
      box.hidden = false;
      box.className = 'status-box ' + (right === qs.length ? 'green' : answered === qs.length ? 'amber' : 'neutral');
      box.innerHTML = '<p><strong>' + right + ' von ' + qs.length + ' richtig.</strong> ' +
        (right === qs.length ? 'Sattelfest – weiter zu Schritt 3.' :
         answered < qs.length ? 'Noch nicht alle Fragen beantwortet.' :
         'Die Erklärungen unter den falschen Antworten zeigen, wo es hakt.') + '</p>';
      store('quiz-done', answered === qs.length ? '1' : '0');
      store('quiz-score', String(right));
    }
    return { right: right, answered: answered, total: qs.length };
  }
  $('#btn-quiz').addEventListener('click', function () { evalQuiz(false); updateAll(); });

  /* ================= Checklisten-Fortschritt ================= */
  function updateProgress() {
    var all = $$('input[data-cl]');
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
    $('#progress-all').style.width = pct + '%';
    $('#progress-all-label').textContent = checkedTotal + ' / ' + all.length + ' (' + pct + ' %)';
    return { done: checkedTotal, total: all.length };
  }

  /* ================= ADR-Rechner ================= */
  function updateADR() {
    var pts = num('adr-n') * num('adr-l');
    var box = $('#adr-result');
    box.className = 'status-box';
    if (pts === 0) {
      box.classList.add('neutral');
      box.innerHTML = '<p>Flaschenzahl und Fassungsraum eintragen.</p>';
    } else if (pts <= 1000) {
      box.classList.add('green');
      box.innerHTML = '<p><strong>≈ ' + pts + ' Punkte – Kleinmenge.</strong> Beförderung mit Erleichterungen: ' +
        'Ladung sichern, Ventilkappen drauf, Fahrzeug belüften, 2-kg-Feuerlöscher an Bord empfohlen.</p>';
    } else {
      box.classList.add('red');
      box.innerHTML = '<p><strong>≈ ' + pts + ' Punkte – über der 1.000-Punkte-Grenze.</strong> Volle ADR-Pflichten ' +
        '(Gefahrgutführerschein, orange Warntafeln, Beförderungspapiere). Praxis-Tipp: liefern lassen statt selbst fahren.</p>';
    }
  }

  /* ================= Betriebsdaten / Generatoren ================= */
  var TAETIGKEIT_TEXT = {
    kfz: 'Kfz-/Motorsport-Werkstatt: Einbau, Wartung und Befüllung von Lachgas-Einspritzsystemen für Kundenfahrzeuge im Rennstreckeneinsatz',
    gastro: 'Gastronomie-/Lebensmittelbetrieb: Einsatz als Treibgas (E942) in der Speisenzubereitung',
    labor: 'Labor/Analytik: Brenngas für die Atomabsorptionsspektrometrie (N₂O-Acetylen-Flamme)',
    industrie: 'Industrie/Fertigung: Einsatz als Prozess-/Oxidationsgas'
  };
  function getBetrieb() {
    var qual = load('radio:qual') === 'e942'
      ? 'Lebensmittelqualität (E942)'
      : 'technisch, Reinheit ≥ 99,5 %';
    return {
      firma: val('f-firma').trim(),
      rechtsform: val('f-rechtsform'),
      ort: val('f-ort').trim(),
      taetigkeit: val('f-taetigkeit'),
      detail: val('f-detail').trim(),
      bedarf: val('f-bedarf'),
      gebinde: val('f-gebinde'),
      name: val('f-name').trim(),
      tel: val('f-tel').trim(),
      qual: qual
    };
  }
  function ph(value, placeholder) {
    return value ? esc(value) : '<span class="placeholder">[' + placeholder + ']</span>';
  }
  function updateBetriebStatus(b) {
    var box = $('#betrieb-status');
    var missing = [];
    if (!b.firma) missing.push('Firmenname');
    if (!b.ort) missing.push('Ort');
    if (!b.taetigkeit) missing.push('Tätigkeit');
    box.className = 'status-box doc-hide-on-print ' + (missing.length ? 'amber' : 'green');
    box.innerHTML = missing.length
      ? '<p>🟡 Für eine vollständige Doku fehlen noch: ' + missing.join(', ') + '.</p>'
      : '<p>✅ Betriebsdaten vollständig – Doku und Anfrage-Mail unten/in Schritt 7 sind fertig befüllt.</p>';
  }
  function updateDoc() {
    var b = getBetrieb();
    updateBetriebStatus(b);
    var taetigkeitText = b.taetigkeit ? TAETIGKEIT_TEXT[b.taetigkeit] : '';
    var heute = new Date().toLocaleDateString('de-DE');
    $('#doc-verwendung').innerHTML =
      '<h4>Dokumentation des Verwendungszwecks – Distickstoffmonoxid (N₂O)</h4>' +
      '<p><strong>' + ph(b.firma, 'Firmenname') + '</strong> (' + esc(b.rechtsform) + '), ' + ph(b.ort, 'Ort') + '</p>' +
      '<p><strong>Tätigkeit:</strong> ' + (taetigkeitText ? esc(taetigkeitText) : '<span class="placeholder">[Tätigkeit wählen]</span>') +
      (b.detail ? ' – ' + esc(b.detail) : '') + '.</p>' +
      '<p><strong>Verwendung:</strong> Das Gas wird ausschließlich für den oben genannten betrieblichen Zweck eingesetzt. ' +
      'Eine Abgabe an Dritte außerhalb der Regeln des Neue-psychoaktive-Stoffe-Gesetzes erfolgt nicht.</p>' +
      '<p><strong>Qualität:</strong> ' + esc(b.qual) + ' · <strong>Gebinde:</strong> ' + esc(b.gebinde) +
      ' · <strong>geschätzter Jahresbedarf:</strong> ca. ' + ph(b.bedarf, 'kg') + ' kg</p>' +
      '<p><strong>Lagerung:</strong> gemäß TRGS 510 – belüftet, über Erdgleiche, gegen Umfallen gesichert, gekennzeichnet. ' +
      'Gefährdungsbeurteilung und Betriebsanweisung liegen vor bzw. werden vor Erstbezug fertiggestellt.</p>' +
      '<p><strong>Ansprechpartner:</strong> ' + ph(b.name, 'Name') + (b.tel ? ', Tel. ' + esc(b.tel) : '') + '</p>' +
      '<p class="doc-sign">' + ph(b.ort, 'Ort') + ', den ' + heute +
      '&nbsp;&nbsp;&nbsp;____________________________<br><span class="fineprint">Unterschrift</span></p>';
  }
  function updateMail() {
    var b = getBetrieb();
    var taetigkeitText = b.taetigkeit ? TAETIGKEIT_TEXT[b.taetigkeit] : '[konkrete Tätigkeit – in Schritt 5 wählen]';
    $('#mail-template').textContent =
      'Betreff: Anfrage ' + (b.qual.indexOf('E942') >= 0 ? 'Lachgas in Lebensmittelqualität (E942)' : 'technisches Lachgas (N₂O)') +
      ' für gewerbliche Nutzung\n\n' +
      'Sehr geehrte Damen und Herren,\n\n' +
      'wir betreiben in ' + (b.ort || '[Ort]') + ' folgendes Gewerbe: ' + taetigkeitText +
      (b.detail ? ' (' + b.detail + ')' : '') + '.\n\n' +
      'Dafür benötigen wir Distickstoffmonoxid (N₂O):\n\n' +
      '  - Qualität:     ' + b.qual + '\n' +
      '  - Gebinde:      ' + b.gebinde + ' (Miete oder Kauf)\n' +
      '  - Jahresbedarf: ca. ' + (b.bedarf || '[XX]') + ' kg\n' +
      '  - Lieferung an: ' + (b.firma || '[Firma]') + ', ' + (b.ort || '[Adresse]') + ' (alternativ Depot-Abholung)\n\n' +
      'Gewerbeanmeldung und eine schriftliche Dokumentation des Verwendungszwecks\n' +
      'liegen vor und senden wir Ihnen gerne zu.\n\n' +
      'Bitte nennen Sie uns ein Angebot inkl. Flaschenmiete/Pfand, Lieferkosten\n' +
      'und etwaiger Mindestabnahmemengen.\n\n' +
      'Mit freundlichen Grüßen\n' +
      (b.name || '[Name]') + (b.firma ? ', ' + b.firma : '') + (b.tel ? ', Tel. ' + b.tel : '');
  }

  /* ================= Kostenrechner & Angebote ================= */
  function updateCalc() {
    var bedarf = num('k-bedarf');
    var gas = bedarf * num('k-preis');
    var miete = num('k-flaschen') * num('k-miete') * 12;
    var liefer = num('k-liefer') * num('k-anzahl');
    var summe = gas + miete + liefer;
    $('#r-gas').textContent = euro(gas);
    $('#r-miete').textContent = euro(miete);
    $('#r-liefer').textContent = euro(liefer);
    $('#r-summe').textContent = euro(summe);
    $('#r-effektiv').textContent = bedarf > 0 ? euro(summe / bedarf) + ' / kg' : '–';
  }
  function updateOffers() {
    var bedarf = num('k-bedarf');
    var offers = [1, 2, 3].map(function (i) {
      var name = val('o' + i + '-name').trim();
      var preis = num('o' + i + '-preis');
      var filled = name !== '' && preis > 0;
      var total = filled ? bedarf * preis + num('o' + i + '-miete') * 12 + num('o' + i + '-liefer') : null;
      return { i: i, name: name, total: total, filled: filled };
    });
    var best = null;
    offers.forEach(function (o) {
      if (o.filled && (best === null || o.total < best.total)) best = o;
    });
    offers.forEach(function (o) {
      var card = $('#offer-' + o.i);
      var totalEl = $('#o' + o.i + '-total');
      totalEl.textContent = o.filled ? euro(o.total) + ' / Jahr' : '–';
      card.classList.toggle('best', best !== null && o.i === best.i && offers.filter(function (x) { return x.filled; }).length > 1);
    });
    var chart = $('#offer-chart');
    var filled = offers.filter(function (o) { return o.filled; });
    if (filled.length < 2) { chart.innerHTML = ''; return { offers: offers, best: best }; }
    var max = Math.max.apply(null, filled.map(function (o) { return o.total; }));
    chart.innerHTML = filled.map(function (o) {
      var w = Math.max(25, Math.round((o.total / max) * 100));
      var cls = best && o.i === best.i ? 'temp-bar best' : 'temp-bar mid';
      return '<div class="temp-row"><span class="temp-label">' + esc(o.name) + '</span>' +
        '<div class="' + cls + '" style="width:' + w + '%">' + euro(o.total) + '</div></div>';
    }).join('');
    return { offers: offers, best: best };
  }

  /* ================= Bestand & Verbrauchs-Log ================= */
  function loadJson(key) {
    try { return JSON.parse(load(key) || '[]'); } catch (e) { return []; }
  }
  function saveJson(key, data) { store(key, JSON.stringify(data)); }

  function renderInventory() {
    var inv = loadJson('inventory');
    var warnLimit = new Date();
    warnLimit.setMonth(warnLimit.getMonth() + 6);
    var warnStr = warnLimit.toISOString().slice(0, 7);
    $('#inv-body').innerHTML = inv.map(function (f, idx) {
      var warn = f.prf && f.prf <= warnStr;
      return '<tr' + (warn ? ' class="warn" title="Prüffrist läuft in unter 6 Monaten ab – beim Tausch ansprechen"' : '') + '>' +
        '<td>' + esc(f.nr) + '</td><td>' + esc(f.size) + '</td>' +
        '<td>' + esc(f.prf || '–') + (warn ? ' ⚠️' : '') + '</td>' +
        '<td>' + esc(f.charge || '–') + '</td>' +
        '<td>' + (f.coa ? '✓' : '–') + '</td><td>' + esc(f.status) + '</td>' +
        '<td><button type="button" class="row-del" data-del-inv="' + idx + '" title="Löschen">✕</button></td></tr>';
    }).join('');
    var aktiv = inv.filter(function (f) { return f.status !== 'leer'; });
    var kg = aktiv.reduce(function (s, f) { return s + (parseFloat(f.size) || 0); }, 0);
    $('#inv-summary').textContent = inv.length
      ? aktiv.length + ' Flasche(n) im Bestand (voll/in Gebrauch), zusammen ca. ' + kg.toLocaleString('de-DE') + ' kg. ⚠️ = Prüffrist < 6 Monate.'
      : 'Noch keine Flaschen erfasst.';
    $$('#inv-body [data-del-inv]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var arr = loadJson('inventory');
        arr.splice(parseInt(btn.getAttribute('data-del-inv'), 10), 1);
        saveJson('inventory', arr);
        renderInventory();
        updateAll();
      });
    });
  }
  function addInventory() {
    var nr = val('inv-nr').trim();
    if (!nr) { $('#inv-nr').focus(); return; }
    var inv = loadJson('inventory');
    inv.push({
      nr: nr, size: val('inv-size'), prf: val('inv-prf'),
      charge: val('inv-charge').trim(), coa: $('#inv-coa').checked, status: val('inv-status')
    });
    saveJson('inventory', inv);
    $('#inv-nr').value = ''; $('#inv-charge').value = ''; $('#inv-coa').checked = false;
    renderInventory();
    updateAll();
  }
  $('#inv-add').addEventListener('click', addInventory);

  function renderLog() {
    var log = loadJson('log');
    $('#log-body').innerHTML = log.map(function (e, idx) {
      return '<tr><td>' + esc(e.datum || '–') + '</td><td>' + esc(e.menge) + '</td><td>' + esc(e.zweck) + '</td>' +
        '<td><button type="button" class="row-del" data-del-log="' + idx + '" title="Löschen">✕</button></td></tr>';
    }).join('');
    var sum = log.reduce(function (s, e) { return s + (parseFloat(e.menge) || 0); }, 0);
    $('#log-summary').textContent = log.length
      ? log.length + ' Einträge, dokumentierter Verbrauch gesamt: ' + sum.toLocaleString('de-DE') + ' kg.'
      : 'Noch keine Verbrauchseinträge.';
    $$('#log-body [data-del-log]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var arr = loadJson('log');
        arr.splice(parseInt(btn.getAttribute('data-del-log'), 10), 1);
        saveJson('log', arr);
        renderLog();
        updateAll();
      });
    });
  }
  function addLog() {
    var zweck = val('log-zweck').trim();
    var menge = val('log-menge');
    if (!menge && !zweck) { $('#log-menge').focus(); return; }
    var log = loadJson('log');
    log.push({ datum: val('log-datum'), menge: menge, zweck: zweck });
    saveJson('log', log);
    $('#log-menge').value = ''; $('#log-zweck').value = '';
    renderLog();
    updateAll();
  }
  $('#log-add').addEventListener('click', addLog);

  function downloadFile(name, mime, content) {
    var blob = new Blob([content], { type: mime });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  }
  function csvLine(cells) {
    return cells.map(function (c) { return '"' + String(c == null ? '' : c).replace(/"/g, '""') + '"'; }).join(';');
  }
  $('#inv-csv').addEventListener('click', function () {
    var rows = [csvLine(['Flaschen-Nr', 'Groesse (kg)', 'Prueffrist', 'Charge', 'CoA', 'Status'])]
      .concat(loadJson('inventory').map(function (f) {
        return csvLine([f.nr, f.size, f.prf, f.charge, f.coa ? 'ja' : 'nein', f.status]);
      }));
    downloadFile('n2o-flaschenbestand.csv', 'text/csv', '﻿' + rows.join('\r\n'));
  });
  $('#log-csv').addEventListener('click', function () {
    var rows = [csvLine(['Datum', 'Menge (kg)', 'Zweck/Auftrag'])]
      .concat(loadJson('log').map(function (e) { return csvLine([e.datum, e.menge, e.zweck]); }));
    downloadFile('n2o-verbrauchslog.csv', 'text/csv', '﻿' + rows.join('\r\n'));
  });

  /* ================= Backup / Import ================= */
  $('#btn-export').addEventListener('click', function () {
    var dump = {};
    Object.keys(localStorage).forEach(function (k) {
      if (k.indexOf(PREFIX) === 0) dump[k.slice(PREFIX.length)] = localStorage.getItem(k);
    });
    downloadFile('n2o-guide-backup.json', 'application/json', JSON.stringify(dump, null, 2));
  });
  $('#btn-import').addEventListener('change', function () {
    var file = this.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var dump = JSON.parse(reader.result);
        Object.keys(dump).forEach(function (k) { store(k, dump[k]); });
        location.reload();
      } catch (e) {
        alert('Datei konnte nicht gelesen werden – ist das ein Guide-Backup (JSON)?');
      }
    };
    reader.readAsText(file);
  });

  /* ================= Drucken ================= */
  function openDetailsAndPrint() {
    $$('details').forEach(function (d) { d.open = true; });
    window.print();
  }
  $('#btn-print').addEventListener('click', openDetailsAndPrint);
  $('#btn-dossier').addEventListener('click', openDetailsAndPrint);
  $('#btn-doc-print').addEventListener('click', function () {
    document.body.classList.add('print-doc');
    window.print();
  });
  window.addEventListener('afterprint', function () {
    document.body.classList.remove('print-doc');
  });

  /* ================= Kopieren ================= */
  $('#btn-copy').addEventListener('click', function () {
    var btn = this;
    navigator.clipboard.writeText($('#mail-template').textContent).then(function () {
      btn.textContent = 'Kopiert ✓';
      setTimeout(function () { btn.textContent = 'Kopieren'; }, 2000);
    }, function () {
      btn.textContent = 'Kopieren fehlgeschlagen';
    });
  });

  /* ================= Zurücksetzen ================= */
  $('#btn-reset').addEventListener('click', function () {
    if (!confirm('Alle Haken, Eingaben, Bestand und Log zurücksetzen?')) return;
    Object.keys(localStorage)
      .filter(function (k) { return k.indexOf(PREFIX) === 0; })
      .forEach(function (k) { localStorage.removeItem(k); });
    location.reload();
  });

  /* ================= Schritt-Status & Score ================= */
  function stepDone(n) {
    switch (n) {
      case 1: return ['w-gewerbe', 'w-taetigkeit', 'w-lager', 'w-doku'].every(function (id) { return $('#' + id).checked; });
      case 2: return load('quiz-done') === '1';
      case 3: return !!load('radio:qual');
      case 4: return $('#recht-ok').checked;
      case 5: { var b = getBetrieb(); return !!(b.firma && b.ort && b.taetigkeit); }
      case 6: { var p = updateProgress(); return p.done === p.total && p.total > 0; }
      case 7: return $('#anfrage-sent').checked;
      case 8: return [1, 2, 3].some(function (i) { return val('o' + i + '-name').trim() !== '' && num('o' + i + '-preis') > 0; });
      case 9: return loadJson('inventory').length > 0;
      default: return false;
    }
  }
  function updateRail() {
    var done = 0;
    $$('#step-rail li').forEach(function (li) {
      var n = parseInt(li.getAttribute('data-goto'), 10);
      var isDone = stepDone(n);
      if (isDone) done++;
      li.classList.toggle('done', isDone);
      li.classList.toggle('current', n === currentStep);
    });
    var pct = Math.round((done / STEP_COUNT) * 100);
    var circ = 163.4;
    $('#ring-fill').style.strokeDashoffset = String(circ * (1 - done / STEP_COUNT));
    $('#ring-label').textContent = pct + '%';
    return done;
  }

  /* ================= Update-Verbund ================= */
  function updateAll() {
    updateWizard();
    updateProgress();
    updateADR();
    updateDoc();
    updateMail();
    updateCalc();
    updateOffers();
    updateRail();
  }

  /* ================= Init ================= */
  renderInventory();
  renderLog();
  updateAll();
  evalQuiz(true);
  setMode(load('mode') || 'guided');

  /* ================= Selbsttest (?selftest=1) ================= */
  if (location.search.indexOf('selftest=1') >= 0) {
    var results = [];
    function assert(name, cond) { results.push((cond ? 'PASS' : 'FAIL') + ' ' + name); }
    try {
      $$('input[type="checkbox"][data-persist]').forEach(function (b) {
        b.checked = true;
        b.dispatchEvent(new Event('change'));
      });
      assert('wizard-green', $('#wizard-result').className.indexOf('green') >= 0);
      assert('checklist-full', updateProgress().done === updateProgress().total);

      $$('.quiz-q').forEach(function (q) {
        var correct = q.querySelector('input[value="' + q.getAttribute('data-correct') + '"]');
        correct.checked = true;
        correct.dispatchEvent(new Event('change'));
      });
      var quiz = evalQuiz(false);
      assert('quiz-7of7', quiz.right === 7 && quiz.total === 7);

      var qualRadio = document.querySelector('input[name="qual"][value="technisch"]');
      qualRadio.checked = true;
      qualRadio.dispatchEvent(new Event('change'));

      [['f-firma', 'Test Motorsport'], ['f-ort', 'Dortmund'], ['f-name', 'Max Test'], ['f-tel', '0231-12345']].forEach(function (p) {
        var el = document.getElementById(p[0]);
        el.value = p[1];
        el.dispatchEvent(new Event('input'));
      });
      var sel = $('#f-taetigkeit');
      sel.value = 'kfz';
      sel.dispatchEvent(new Event('change'));
      assert('doc-has-firma', $('#doc-verwendung').textContent.indexOf('Test Motorsport') >= 0);
      assert('mail-has-qual', $('#mail-template').textContent.indexOf('99,5') >= 0);
      assert('betrieb-green', $('#betrieb-status').className.indexOf('green') >= 0);

      [['o1-name', 'Anbieter A'], ['o2-name', 'Anbieter B']].forEach(function (p) {
        var el = document.getElementById(p[0]);
        el.value = p[1];
        el.dispatchEvent(new Event('input'));
      });
      [['o1-preis', '20'], ['o2-preis', '15'], ['o1-miete', '16'], ['o2-miete', '20']].forEach(function (p) {
        var el = document.getElementById(p[0]);
        el.value = p[1];
        el.dispatchEvent(new Event('input'));
      });
      var offers = updateOffers();
      assert('offer-best-is-2', offers.best && offers.best.i === 2);
      assert('offer-chart-bars', $('#offer-chart').children.length === 2);

      $('#adr-n').value = '25'; $('#adr-l').value = '50';
      $('#adr-n').dispatchEvent(new Event('input'));
      assert('adr-over-limit', $('#adr-result').className.indexOf('red') >= 0);
      $('#adr-n').value = '2';
      $('#adr-n').dispatchEvent(new Event('input'));
      assert('adr-small', $('#adr-result').className.indexOf('green') >= 0);

      $('#inv-nr').value = 'WF-001'; $('#inv-prf').value = '2027-06';
      addInventory();
      assert('inventory-row', loadJson('inventory').length === 1);
      $('#log-menge').value = '2.5'; $('#log-zweck').value = 'Testauftrag';
      addLog();
      assert('log-row', loadJson('log').length === 1);

      var doneSteps = updateRail();
      assert('steps-done-8plus', doneSteps >= 8);
    } catch (e) {
      results.push('FAIL exception: ' + e.message);
    }
    var failed = results.filter(function (r) { return r.indexOf('FAIL') === 0; });
    document.title = 'SELFTEST ' + (failed.length ? 'FAIL' : 'PASS') + ' ' +
      (results.length - failed.length) + '/' + results.length + ' | ' + results.join(' | ');
  }
})();
