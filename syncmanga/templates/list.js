// =============================================================================
//  Manga-Leseliste - Interaktivitaet (Filter, Sortierung, Archiv, Broken-Report)
//  -----------------------------------------------------------------------------
//  LESBARE Quelle. render.py bettet sie ueber _minify_js() ein (nur Kommentare/
//  Leerzeilen weg, KEIN Zeilen-Zusammenziehen -> Verhalten 1:1). Alle Daten
//  stehen in data-* Attributen je <tr> (vom Renderer gesetzt):
//    data-n = Name (klein) · data-au = Autor · data-s = Fortschrittswort
//    data-help = "1" braucht Hilfe · data-medium = Typ · data-dyn = Webtoon
//    data-gen = Genres (space-getrennt) · data-adult = sexual/gore · data-h = Archiv-Key
//  Cell-Indizes: 0 Serie · 3 Kapitel(data-un=ungelesen) · 4 Zuletzt(data-ts) · 6 Bewertung(data-rt)
// =============================================================================

// --- Zustands-Sicherung (JB): fehlt der Browser-Zustand (neuer Browser / Website-Daten geloescht),
// aus dem vom Renderer eingebetteten SEED (data/list_state.json = 💾-Export) wiederherstellen. ---
var STATE_KEYS=['mangaArchived','mangaFav','titleCfm','brk','hcols','nsfw','chapFix','dense','theme','tiles','pausedReaders'];
(function(){try{var S=(typeof SEED!=='undefined')?SEED:null;if(!S)return;STATE_KEYS.forEach(function(k){if(localStorage.getItem(k)===null&&S[k]!=null)localStorage.setItem(k,S[k])})}catch(e){}})();
// --- Schluessel-Migration (JB Runde 35, "Mein Archiv hat sich resetted"): data-h ist jetzt ein
// STABILER Schluessel (DB-ID bzw. n:+Roh-Verlaufsname) statt norm(Anzeigetitel) — Titelkorrekturen
// aendern ihn nie mehr. Alte gespeicherte Schluessel (norm alter Titel) werden hier ueber die vom
// Renderer eingebettete Alias-Map MIG umgeschrieben. Idempotent (neue Keys stehen nicht in MIG),
// unbekannte Keys bleiben unangetastet, laeuft VOR dem Einlesen von ARCH/FAV. ---
(function(){try{var M=(typeof MIG!=='undefined')?MIG:null;if(!M)return;var mp=function(k){return M[k]||k};
['mangaArchived','mangaFav'].forEach(function(sk){var v=localStorage.getItem(sk);if(!v)return;var b=[];JSON.parse(v).forEach(function(k){k=mp(k);if(b.indexOf(k)<0)b.push(k)});var nv=JSON.stringify(b);if(nv!==v)localStorage.setItem(sk,nv)});
['titleCfm','chapFix'].forEach(function(sk){var v=localStorage.getItem(sk);if(!v)return;var o=JSON.parse(v),out={},ch=false;Object.keys(o).forEach(function(k){var nk=mp(k);if(nk!==k)ch=true;if(!(nk in out))out[nk]=o[k]});if(ch)localStorage.setItem(sk,JSON.stringify(out))})}catch(e){}})();
// 💾-Export: kompletten Zustand als list_state.json sichern (nach Manga/data legen -> Auto-Restore).
function saveState(){var o={};STATE_KEYS.forEach(function(k){var v=localStorage.getItem(k);if(v!==null)o[k]=v});var b=new Blob([JSON.stringify(o,null,1)],{type:'application/json'}),u=URL.createObjectURL(b),el=document.createElement('a');el.href=u;el.download='list_state.json';el.click();URL.revokeObjectURL(u)}

// --- Zustand + Start: Filter-Flags, veraltete Keys aufraeumen, Archiv-Set laden ---
var flt='',helpOnly=false,newOnly=false;['mangaHidden','mangaDeleted'].forEach(k=>localStorage.removeItem(k));var ARCH=new Set(JSON.parse(localStorage.getItem('mangaArchived')||'[]'));

// Archiv-Set (Menge der data-h) in localStorage sichern
function saveArch(){try{localStorage.setItem('mangaArchived',JSON.stringify([...ARCH]))}catch(e){}}

// --- ap(r): entscheidet, ob EINE Zeile sichtbar ist (alle aktiven Filter kombiniert) ---
// t = Suchtext, b = Titel enthaelt Suchtext, isA = archiviert.
function ap(r){if(favHidden&&FAV.has(r.dataset.h)){r.style.display='none';return}   // Favoriten ausgeblendet?
var t=q.value.toLowerCase(),b=r.cells[0].textContent.toLowerCase().includes(t),isA=ARCH.has(r.dataset.h);
// Archiv-Ansicht: ALLE archivierten zeigen (nur die Textsuche greift) - Genre/Typ/Status/NSFW duerfen
// hier NICHT filtern (sonst "7 im Archiv, nur 1 sichtbar"). Sonst: alle Filter, nur NICHT-archivierte.
if(document.body.classList.contains('archview')){r.style.display=(isA&&b)?'':'none';return}
var cc=r.querySelector('.c'),c=cf.value,a=!flt||(r.dataset.s||'').includes(flt),d=!c||(c==='Webtoon'?r.dataset.dyn==='1':(r.dataset.medium||'')===c),hp=!helpOnly||r.dataset.help==='1',nw=!newOnly||(cc&&(cc.dataset.un-0)>0),gg=gmatch(r),ns=!nf.value||(nf.value==='both'?!r.dataset.adult:r.dataset.adult!==nf.value);r.style.display=(a&&b&&d&&hp&&nw&&gg&&ns&&!isA)?'':'none'}

// --- Genre-Mehrfachfilter (3 Zustaende, JB): 1x Klick = NUR dieses Genre (gruen), 2x = Genre
// AUSBLENDEN (rot, durchgestrichen), 3x = neutral. gmatch = alle gewaehlten UND keins der Ausschluesse.
var GSEL=new Set(),GEXC=new Set();
function gmatch(r){var s=' '+(r.dataset.gen||'')+' ';for(var g of GSEL){if(s.indexOf(' '+g+' ')<0)return false}for(var g of GEXC){if(s.indexOf(' '+g+' ')>=0)return false}return true}
function toggleGenre(el){var g=el.dataset.g;if(GSEL.has(g)){GSEL.delete(g);GEXC.add(g);el.classList.remove('on');el.classList.add('ex')}else if(GEXC.has(g)){GEXC.delete(g);el.classList.remove('ex')}else{GSEL.add(g);el.classList.add('on')}regray();ff()}

// --- regray(): Live-Counts je Genre/Filter neu zaehlen + Buttons mit 0 Treffern ausgrauen ---
// (beruecksichtigt die bereits gewaehlten Genres, damit man sich nicht in "nichts angezeigt" filtert)
function regray(){var rows=[].slice.call(document.querySelectorAll('#t tbody tr'));document.querySelectorAll('#gf .gchip').forEach(function(c){var g=c.dataset.g,n=0;for(var i=0;i<rows.length;i++){var r=rows[i];if(gmatch(r)&&(' '+(r.dataset.gen||'')+' ').indexOf(' '+g+' ')>=0)n++}var ic=c.querySelector('i');if(ic)ic.textContent=n;c.classList.toggle('off',!GSEL.has(g)&&!GEXC.has(g)&&n===0)});
var pf=document.getElementById('pf');if(pf){[].forEach.call(pf.options,function(o){var base=o.dataset.l||(o.dataset.l=o.textContent.replace(/ \(\d+\)$/,''));var f=o.value;var n=0;for(var i=0;i<rows.length;i++){var r=rows[i];if(!gmatch(r))continue;if(!f||(r.dataset.s||'').indexOf(f)>=0)n++}o.textContent=base+' ('+n+')';o.disabled=(!!f&&n===0&&pf.value!==f)})}
var hb=document.getElementById('hb');if(hb){var nh=0;for(var i=0;i<rows.length;i++){if(gmatch(rows[i])&&rows[i].dataset.help==='1')nh++}hb.classList.toggle('off',nh===0)}
var nb=document.getElementById('nb');if(nb){var nn=0;for(var i=0;i<rows.length;i++){var c3=rows[i].querySelector('.c');if(gmatch(rows[i])&&c3&&(c3.dataset.un-0)>0)nn++}nb.classList.toggle('off',nn===0)}}

// --- Filter anwenden/umschalten ---
// ff = alle Zeilen neu bewerten · fs = Fortschritts-Filter setzen · fh = nur "braucht Hilfe"
// fn = nur mit neuen Kapiteln · setNsfw = 18+-Wahl merken
function ff(){document.querySelectorAll('#t tbody tr').forEach(ap);if(document.body.classList.contains('tiles'))buildTiles()}
// qf = entprellte Variante fuer die TIPP-Suche: bei 776 Zeilen nicht bei jedem Tastendruck neu
// filtern, sondern erst 120ms nach der letzten Eingabe -> fluessiges Tippen. (Buttons bleiben instant.)
var qt;function qf(){clearTimeout(qt);qt=setTimeout(ff,120)}
// Fortschritts-Filter als EIN Dropdown (JB: 6 Knoepfe brachen die Zeile um; fs()/fbtn entfernt)
function fsSel(sel){flt=sel.value;ff()}
function fh(b){helpOnly=!helpOnly;b.classList.toggle('on',helpOnly);ff()}
function fn(b){newOnly=!newOnly;b.classList.toggle('on',newOnly);ff()}
function setNsfw(sel){try{localStorage.setItem('nsfw',sel.value)}catch(e){}ff()}
// NSFW-Wahl aus localStorage wiederherstellen
(function(){try{var nm=localStorage.getItem('nsfw')||'',nfe=document.getElementById('nf');if(nm&&nfe)nfe.value=nm}catch(e){}})();

// --- Archiv: einzelne Serie togglen; Modus/Ansicht umschalten; Zaehler = vorhandene archivierte ---
function arch(k){if(ARCH.has(k))ARCH.delete(k);else ARCH.add(k);saveArch();ff();updateAb()}
function toggleArchmode(){var on=document.body.classList.toggle('archmode');ab.classList.toggle('on',on);if(on){document.body.classList.remove('archview');vb.classList.remove('on')}ff()}
function toggleArchview(){var on=document.body.classList.toggle('archview');vb.classList.toggle('on',on);if(on){document.body.classList.remove('archmode');ab.classList.remove('on')}ff()}
function updateAb(){var n=0;document.querySelectorAll('#t tbody tr').forEach(function(r){if(ARCH.has(r.dataset.h))n++});vb.textContent=((typeof I!=='undefined'&&I.arch)||'🗃 Archiv')+': '+n}

// --- Spalten ein/ausblenden (Menue "Spalten" neben den Panels): body.hc<n> versteckt Spalte n (2..7) ---
function toggleCol(n,cb){document.body.classList.toggle('hc'+n,!cb.checked);var h=[];for(var i=2;i<=7;i++){if(document.body.classList.contains('hc'+i))h.push(i)}try{localStorage.setItem('hcols',JSON.stringify(h))}catch(e){}refreezeHead()}
// gespeicherte Spalten-Wahl wiederherstellen (versteckte Spalte -> Checkbox #col<n> leer)
(function(){try{JSON.parse(localStorage.getItem('hcols')||'[]').forEach(function(n){document.body.classList.add('hc'+n);var cb=document.getElementById('col'+n);if(cb)cb.checked=false})}catch(e){}})();

// --- Favoriten (wie Archiv: erst "Favorit"-Modus einschalten, dann ⭐ je Zeile klicken). ---
// FAV = Set der data-h. Standardmaessig EINGEBLENDET.
var FAV=new Set(JSON.parse(localStorage.getItem('mangaFav')||'[]')),favHidden=false,usort=false;
function saveFav(){try{localStorage.setItem('mangaFav',JSON.stringify([...FAV]))}catch(e){}}
// Zaehler am "⭐ Favoriten: N"-Button aktualisieren
function updateFav(){var b=document.getElementById('vfb');if(b)b.textContent='⭐ '+((typeof I!=='undefined'&&I.fav)||'Favoriten')+': '+FAV.size}
// eine Serie als Favorit togglen (⭐-Klick im Favorit-Modus): merken, Zeilen markieren, anpinnen, Zaehler, Filter
function fav(k){if(FAV.has(k))FAV.delete(k);else FAV.add(k);saveFav();document.querySelectorAll('#t tbody tr').forEach(function(r){r.classList.toggle('fav',FAV.has(r.dataset.h))});pinFavs(!usort);updateFav();ff()}
// pinFavs(): Favoriten getrennt nach OBEN. sortDefault=true -> nach ungelesen(data-un) desc, dann Bewertung
// (data-rt) desc; sonst AKTUELLE Reihenfolge behalten (folgt so der aktiven Spalten-Sortierung).
function pinFavs(sortDefault){var tb=document.querySelector('#t tbody'),f=[...tb.rows].filter(function(r){return FAV.has(r.dataset.h)});if(sortDefault){f.sort(function(a,b){var ca=a.querySelector('.c'),cb=b.querySelector('.c'),ua=ca?ca.dataset.un-0:0,ub=cb?cb.dataset.un-0:0;if(ub!==ua)return ub-ua;var ra=a.querySelector('.rt'),rb=b.querySelector('.rt');return (rb?rb.dataset.rt-0:0)-(ra?ra.dataset.rt-0:0)})}f.reverse().forEach(function(r){tb.insertBefore(r,tb.firstChild)});if(document.body.classList.contains('tiles'))buildTiles()}
// Favorit-MODUS (Sterne zum Anklicken zeigen) bzw. Favoriten EIN-/AUSBLENDEN
function toggleFavmode(){var on=document.body.classList.toggle('favmode');document.getElementById('fm').classList.toggle('on',on)}
function toggleFavview(btn){favHidden=!favHidden;btn.classList.toggle('dim',favHidden);ff()}
function reSortDefault(){usort=false;var tb=document.querySelector('#t tbody'),rs=[...tb.rows];rs.sort(function(a,b){var ra=a.querySelector('.rt'),rb=b.querySelector('.rt'),d=(rb?rb.dataset.rt-0:-1)-(ra?ra.dataset.rt-0:-1);return d||(a.dataset.n||'').localeCompare(b.dataset.n||'')});rs.forEach(function(r){tb.appendChild(r)});pinFavs(true)}

// --- Sortierung: s(i) nach Spalte i (Zahlenspalten numerisch), sortAuthor nach data-au; Klick toggelt Richtung ---
// Sortierung nach Spalte i. Der Spalten-TYP wird an der Zellen-KLASSE erkannt (.c Kapitel/ungelesen,
// .d Zuletzt/Zeitstempel, .rt Bewertung) -> robust gegen Spalten-Verschiebungen (z.B. neue ⭐-Spalte).
var dir=1;function s(i){usort=true;var tb=document.querySelector('#t tbody'),rs=[...tb.rows];dir*=-1;rs.sort((a,b)=>{var x=a.cells[i],y=b.cells[i];if(i==0)return((a.dataset.n||'').localeCompare(b.dataset.n||''))*dir;if(x.classList.contains('c'))return((x.dataset.un-0)-(y.dataset.un-0))*dir;if(x.classList.contains('d'))return(x.dataset.ts-y.dataset.ts)*dir;if(x.classList.contains('rt'))return(x.dataset.rt-y.dataset.rt)*dir;return x.textContent.localeCompare(y.textContent)*dir});rs.forEach(r=>tb.appendChild(r));pinFavs()}
function sortAuthor(){usort=true;var tb=document.querySelector('#t tbody'),rs=[...tb.rows];dir*=-1;rs.sort((a,b)=>(a.dataset.au||'').localeCompare(b.dataset.au||'')*dir);rs.forEach(r=>tb.appendChild(r));pinFavs()}

// --- Lesestand manuell setzen (JB): Klick auf die Kapitel-Zelle -> Zahl eingeben. NUR Zahlen wirken;
// Abbrechen/Unsinn aendert nichts; leere Eingabe setzt auf den Scan-Stand zurueck. Gespeichert in
// localStorage 'chapFix' (wandert in 💾-Sicherung + Export via data-rc). ---
function cfGet(){try{return JSON.parse(localStorage.getItem('chapFix')||'{}')}catch(e){return{}}}
function cfSave(o){localStorage.setItem('chapFix',JSON.stringify(o))}
// Kapitel-Nummer in einer Reader-URL austauschen (chapter-16, /chapter/16, episode_no=7 ...) ->
// die AKTION-Spalte folgt dem manuell gesetzten Lesestand (JB-Wunsch).
function cfRelink(tr,n){var a=tr.querySelector('a.pill.go');if(!a)return;if(a.dataset.orighref==null)a.dataset.orighref=a.href;var u=a.dataset.orighref;var v=u.replace(/((?:chapter|episode|chap|ch)[-_\/]?)(\d+(?:[.-]\d+)?)/i,function(m,p){return p+n}).replace(/([?&]episode_no=)\d+/i,function(m,p){return p+n});if(v!==u)a.href=v}
function cfUnlink(tr){var a=tr.querySelector('a.pill.go');if(a&&a.dataset.orighref!=null)a.href=a.dataset.orighref}
function cfSet(td,n){var tr=td.closest('tr');if(td.dataset.orig==null){td.dataset.orig=td.innerHTML;td.dataset.origun=td.dataset.un;td.dataset.origrc=tr.dataset.rc}var lat=parseFloat(td.dataset.lat)||0;if(lat>0&&n>lat)n=lat;var badge=td.querySelector('span.unk'),bh=badge?badge.outerHTML:'',fmt=function(x){return x%1?x:Math.round(x)};td.innerHTML=fmt(n)+' / '+(lat>n?fmt(lat):(fmt(n)||'?'))+bh;td.dataset.un=Math.max(0,Math.round((lat||n)-n));tr.dataset.rc=Math.floor(n);cfRelink(tr,fmt(n));return n}
function cfReset(td){var tr=td.closest('tr');if(td.dataset.orig!=null){td.innerHTML=td.dataset.orig;td.dataset.un=td.dataset.origun;tr.dataset.rc=td.dataset.origrc;cfUnlink(tr)}}
function chapEdit(td){var tr=td.closest('tr'),k=tr.dataset.h,o=cfGet(),cur=(o[k]!=null?o[k]:tr.dataset.rc||'');var v=prompt((typeof I!=='undefined'&&I.cq)||'Gelesen bis Kapitel?',cur);if(v===null)return;v=String(v).trim().replace(',','.');if(v===''){if(o[k]!=null){delete o[k];cfSave(o);cfReset(td);ff()}return}var n=parseFloat(v);if(!isFinite(n)||n<0)return;n=cfSet(td,n);o[k]=n;cfSave(o);ff()}
function applyChapFix(){var o=cfGet();document.querySelectorAll('#t tbody tr').forEach(function(tr){var n=o[tr.dataset.h];if(n!=null){var td=tr.querySelector('td.c');if(td)cfSet(td,parseFloat(n))}})}
document.addEventListener('click',function(ev){var td=ev.target.closest('td.c');if(td)chapEdit(td)});

// --- 🎲 Ueberrasch mich (JB): zufaellige UNGELESENE Serie (Backlog), Bewertung gewichtet ---
function luckyPick(){var rows=[...document.querySelectorAll('#t tbody tr')].filter(function(r){return r.style.display!=='none'&&(parseInt(r.dataset.rc||'0',10)||0)===0&&!ARCH.has(r.dataset.h)});if(!rows.length)return;var tot=0,w=rows.map(function(r){var rt=r.querySelector('.rt'),v=rt?(parseFloat(rt.dataset.rt)||5):5;tot+=v;return v});var x=Math.random()*tot,i=0;while(x>w[i]&&i<w.length-1){x-=w[i];i++}var r=rows[i];r.scrollIntoView({behavior:'smooth',block:'center'});r.classList.add('lucky');setTimeout(function(){r.classList.remove('lucky')},2400);var a=r.querySelector('a.pill.go');if(a)window.open(a.href,'_blank')}

// --- ☀/🌙 Tag/Nacht (JB): manueller Schalter; ohne gespeicherte Wahl zaehlt die OS-Einstellung.
// Knopf zeigt immer das ZIEL (im Dunkeln ☀ = "mach hell"). Wahl persistent ('theme' + 💾-Sicherung). ---
// Text-Glyphen ☀/☾ statt Emoji -> der Knopf bleibt IMMER gelb einfaerbbar (JB-Wunsch)
function thApply(l){document.body.classList.toggle('light',l);var b=document.getElementById('thm');if(b)b.textContent=l?'☾':'☀'}
function toggleTheme(){var l=!document.body.classList.contains('light');thApply(l);try{localStorage.setItem('theme',l?'light':'dark')}catch(e){}}
function applyTheme(){var t=null;try{t=localStorage.getItem('theme')}catch(e){}var l=t?t==='light':!!(window.matchMedia&&matchMedia('(prefers-color-scheme:light)').matches);thApply(l)}

// --- Kompakt-Modus (JB): schmalere Zeilen; Zustand persistent (localStorage 'dense' + 💾-Sicherung) ---
function toggleDense(){var on=document.body.classList.toggle('dense');try{localStorage.setItem('dense',on?'1':'')}catch(e){}var b=document.getElementById('dns');if(b)b.classList.toggle('on',on);refreezeHead()}
function applyDense(){if(localStorage.getItem('dense')){document.body.classList.add('dense');var b=document.getElementById('dns');if(b)b.classList.add('on')}}

// --- Reader-Pausen (JB Runde 37, MangaFire-Umbau): nicht pruefbare Seiten manuell pausieren.
// Server-Default aus sources.json (I.paused); der Nutzer kann im ⏸-Menue je Seite umschalten
// (localStorage 'pausedReaders' = {teilstring: 1|0}, 1 pausiert zusaetzlich, 0 hebt Server-Pause auf).
// applyPause() lenkt NUR die Anzeige um: Aktions-Link je Zeile = erster nicht-pausierter Kandidat
// aus [Ex-Primaerlink (data-pp) > aktueller Primaerlink > Alt-Reserven]. Nichts geht verloren. ---
function pausedGet(){try{return JSON.parse(localStorage.getItem('pausedReaders')||'{}')}catch(e){return{}}}
function pausedEff(){var m={},ov=pausedGet();((typeof I!=='undefined'&&I.paused)||[]).forEach(function(p){m[p]=1});Object.keys(ov).forEach(function(k){if(ov[k])m[k]=1;else delete m[k]});return Object.keys(m)}
function hostPaused(u,P){var h='';try{h=new URL(u,location.href).hostname.toLowerCase()}catch(e){return false}
return P.some(function(p){return p&&h.indexOf(p)>=0})}
function togglePause(cb){var ov=pausedGet(),srv=((typeof I!=='undefined'&&I.paused)||[]);
// ALLE passenden Server-Teilstrings uebersteuern, nicht nur den ersten (JB Runde 44:
// 'mangafire' manuell + 'mangafire.to' auto gleichzeitig -> Abhaken hob nur einen auf,
// der andere hielt die Pause und der Haken sprang sofort zurueck).
cb.dataset.ph.split(',').forEach(function(p){if(!p)return;var subs=srv.filter(function(x){return p.indexOf(x)>=0});if(!subs.length)subs=[p];subs.forEach(function(sub){ov[sub]=cb.checked?1:0})});
try{localStorage.setItem('pausedReaders',JSON.stringify(ov))}catch(e){}applyPause()}
function applyPause(){var P=pausedEff();
document.querySelectorAll('#t tbody tr').forEach(function(r){var act=r.querySelector('td.act');if(!act)return;var prim=act.querySelector('a.pill.go');if(!prim)return;
if(!prim.dataset.op){prim.dataset.op=prim.getAttribute('href');prim.dataset.ol=prim.textContent}
var alts=[].slice.call(act.querySelectorAll('details.alt a.pill.go')).filter(function(a){return !a.classList.contains('galt')});
var cands=[];alts.forEach(function(a){if(a.dataset.pp)cands.push([a.getAttribute('href'),(typeof I!=='undefined'&&I.op)||'▶ öffnen'])});
cands.push([prim.dataset.op,prim.dataset.ol]);
alts.forEach(function(a){if(!a.dataset.pp)cands.push([a.getAttribute('href'),(typeof I!=='undefined'&&I.op)||'▶ öffnen'])});
var pick=null;for(var i=0;i<cands.length;i++){if(cands[i][0]&&!hostPaused(cands[i][0],P)){pick=cands[i];break}}
// Sind ALLE Lese-Quellen pausiert, ist die letzte Instanz die Kombi-SUCHE (a.gsr) — NICHT
// die pausierte Original-Quelle (JB-Bug: A pausiert -> B, B pausiert -> sprang zurueck zu A).
// Alternative/Suche ganz unten: erst wenn wirklich alles pausiert ist.
if(!pick){var gs=r.querySelector('a.gsr');
  pick=(gs&&gs.getAttribute('href'))?[gs.getAttribute('href'),prim.dataset.ol]:[prim.dataset.op,prim.dataset.ol];}
// Label bleibt IMMER das Zustands-Label (JB Runde 42: anfangen/weiterlesen/beendet haengt
// an der Serie, nicht an der Quelle) — beim Quellen-Tausch aendert sich nur das Ziel.
prim.setAttribute('href',pick[0]);prim.textContent=prim.dataset.ol;
// Quelle-Spalte folgt dem TATSAECHLICHEN Ziel (JB Runde 38: 'Anzeige sollte zeigen wohin
// der Knopf hinfuehrt'): beim Tausch den Host des gezeigten Links anzeigen, sonst Original.
var sc=r.querySelector('td.src');
if(sc){if(sc.dataset.os===undefined)sc.dataset.os=sc.innerHTML;
if(pick[0]===prim.dataset.op){sc.innerHTML=sc.dataset.os}
else{var sh='';try{sh=new URL(pick[0],location.href).hostname.replace(/^www\./,'')}catch(e){}
var st=sh.length>22?sh.slice(0,21)+'…':sh;sc.innerHTML='<span title="'+sh+'">'+st+'</span>'}}});
// Ampel-Chips live nachziehen: ⏸ fuer pausierte Hosts (in der vorhandenen Ampelfarbe), sonst ●
document.querySelectorAll('.srcchip[data-rh]').forEach(function(c){var d=c.querySelector('.dot');if(!d)return;var on=P.some(function(p){return p&&(c.dataset.rh||'').indexOf(p)>=0});d.textContent=on?'⏸':'●'});
// ⏸-Menue-Haken synchron halten (data-ph kann eine Komma-Liste sein: Familie/Sammelgruppe —
// Haken = ALLE Teile pausiert)
document.querySelectorAll('input[data-ph]').forEach(function(cb){var parts=cb.dataset.ph.split(',').filter(Boolean);cb.checked=parts.length>0&&parts.every(function(q){return P.some(function(p){return p&&q.indexOf(p)>=0})})})}

// --- Listen-Export (3b Etappe 1): MAL-XML (fuer MyAnimeList/AniList-Import -> MangaBaka zieht von
// dort) + Roh-JSON. Optionen: Archivierte mitnehmen / nur Favoriten. Kapitelstand = gedeckelter Wert
// (data-rc), Status = MAL-Vokabular (data-mst). Zeilen ohne MAL-ID werden gezaehlt + gemeldet. ---
function xRows(){var wa=document.getElementById('xarch').checked,fo=document.getElementById('xfav').checked;return [...document.querySelectorAll('#t tbody tr')].filter(function(tr){var k=tr.dataset.h;if(!wa&&ARCH.has(k))return false;if(fo&&!FAV.has(k))return false;return true})}
function xDown(txt,mime,fname){var b=new Blob([txt],{type:mime}),u=URL.createObjectURL(b),el=document.createElement('a');el.href=u;el.download=fname;el.click();URL.revokeObjectURL(u)}
function exportMal(){var out=[],skip=0;xRows().forEach(function(tr){var id=tr.dataset.mal;if(!id){skip++;return}var name=(tr.dataset.n||'').replace(/\]\]>/g,']]]]><![CDATA[>');out.push('<manga><series_mangadb_id>'+id+'</series_mangadb_id><series_title><![CDATA['+name+']]></series_title><my_read_chapters>'+(parseInt(tr.dataset.rc||'0',10)||0)+'</my_read_chapters><my_score>0</my_score><my_status>'+(tr.dataset.mst||'Reading')+'</my_status><update_on_import>1</update_on_import></manga>')});var xml='<?xml version="1.0" encoding="UTF-8" ?>\n<myanimelist>\n<myinfo><user_export_type>2</user_export_type></myinfo>\n'+out.join('\n')+'\n</myanimelist>';xDown(xml,'application/xml','manga_leseliste_mal.xml');alert(out.length+' '+((typeof I!=='undefined'&&I.xd)||'exportiert')+(skip?('\n'+skip+' '+((typeof I!=='undefined'&&I.xs)||'ohne MAL-ID übersprungen')):''))}
function exportJson(){var out=xRows().map(function(tr){return {name:tr.dataset.n,read:parseInt(tr.dataset.rc||'0',10)||0,status:tr.dataset.mst||'',mal_id:tr.dataset.mal||null,fav:FAV.has(tr.dataset.h),archived:ARCH.has(tr.dataset.h)}});xDown(JSON.stringify(out,null,1),'application/json','manga_leseliste.json');alert(out.length+' '+((typeof I!=='undefined'&&I.xd)||'exportiert'))}

// --- ⤵ Import-Knopf (JB): MAL-XML direkt im Browser einlesen. Bekannte Serien (data-mal) ->
// Lesestand sofort anheben (chapFix, nie senken); unbekannte -> imported_series.json zum Download
// (nach Manga/data legen, der naechste Lauf reichert sie an). ---
// jsNorm MUSS syncmanga/parse.norm() spiegeln (gleiche Keys, sonst Duplikat-Zeilen beim Merge).
function jsNorm(s){s=String(s||'').toLowerCase().replace(/['’]/g,'');s=s.replace(/\b(?:chapter|chap|episode|ep|ch|vol|volume|season)\.?\s*\d+(?:\.\d+)?/g,' ');s=s.replace(/\b(20\d\d|the|a|an|s\d|official|manga|manhwa|manhua|webtoon)\b/g,'');return s.replace(/[^a-z0-9]/g,'')}
function importMal(inp){var f=inp.files&&inp.files[0];inp.value='';if(!f)return;var rd=new FileReader();rd.onload=function(){try{var doc=new DOMParser().parseFromString(rd.result,'text/xml');var byMal={};document.querySelectorAll('#t tbody tr').forEach(function(tr){if(tr.dataset.mal)byMal[tr.dataset.mal]=tr});var o=cfGet(),up=0,unknown=[];[].forEach.call(doc.querySelectorAll('manga'),function(m){var g=function(t){var el=m.querySelector(t);return el?(el.textContent||'').trim():''};var id=g('series_mangadb_id')||g('manga_mangadb_id');var ch=parseFloat(g('my_read_chapters'))||0;var tr=byMal[id];if(tr){var k=tr.dataset.h,cur=parseFloat(o[k]!=null?o[k]:tr.dataset.rc)||0;if(ch>cur){var td=tr.querySelector('td.c');o[k]=td?cfSet(td,ch):ch;up++}}else if(g('series_title')){unknown.push({t:g('series_title'),c:ch||null,s:g('my_status')||'Reading',m:parseInt(id,10)||null})}});cfSave(o);ff();var msg=up+' '+((typeof I!=='undefined'&&I.imu)||'Lesestände übernommen');if(unknown.length){var obj={};unknown.forEach(function(u){var k=jsNorm(u.t);if(k&&!obj[k])obj[k]={name:u.t,chap:u.c,status:u.s==='Completed'?'Fertig':(u.s==='Reading'?'Am Lesen':'Gelesen'),mal_id:u.m}});xDown(JSON.stringify(obj,null,1),'application/json','imported_series.json');msg+='\n'+unknown.length+' '+((typeof I!=='undefined'&&I.imn)||'unbekannte Serien → imported_series.json (nach Manga/data legen)')}alert(msg)}catch(e){alert('Import: '+e)}};rd.readAsText(f)}

// --- ▦ Kachel-Ansicht (JB): Cover-Galerie, komplett CLIENTSEITIG aus den Tabellen-Zeilen gebaut
// (kein HTML-Gewicht; Bilder laden lazy). Zahl links = dein Stand in der USER-Status-Farbe,
// Zahl rechts = Gesamt in der VERLAGS-Status-Farbe. Klick aufs Cover = weiterlesen/öffnen. ---
var PUBC={'Laufend':'pOn','Ongoing':'pOn','Abgeschlossen':'pDone','Completed':'pDone','Pausiert':'pHia','Hiatus':'pHia','On Hiatus':'pHia','Abgebrochen':'pStop','Cancelled':'pStop','Angekündigt':'pSoon','Upcoming':'pSoon'};
function tileName(td){var nm=td&&td.querySelector('.nmline');if(!nm)return'';var t='';for(var i=0;i<nm.childNodes.length;i++){var n=nm.childNodes[i];if(n.nodeType===3)t+=n.textContent}return t.trim()}
// Das Grid kommt HINTER .wrap (JB-Fund: davor eingefuegt lag die Kopf-Sortierleiste unsichtbar
// UNTER 789 Kacheln am Seitenende) -> der Tabellen-Kopf bleibt OBEN stehen und sortiert die Kacheln.
function buildTiles(){refreezeHead();var c=document.getElementById('tiles');if(!c){c=document.createElement('div');c.id='tiles';var w=document.querySelector('.wrap');w.parentNode.insertBefore(c,w.nextSibling)}var out=[];var anyFav=false,sepDone=false;document.querySelectorAll('#t tbody tr').forEach(function(tr){if(tr.style.display==='none')return;
// Favoriten-Trenner (JB): Favoriten stehen gepinnt oben — vor der ersten NICHT-Favoriten-
// Kachel kommt EINE Linie ueber die volle Breite (entfaellt, wenn Favoriten ausgeblendet sind).
var isFav=FAV.has(tr.dataset.h);if(isFav)anyFav=true;else if(anyFav&&!sepDone){out.push('<div class=tsep></div>');sepDone=true}var td=tr.cells[0],a=tr.querySelector('a.pill.go'),cc=tr.querySelector('td.c'),st=tr.querySelector('td.st'),pub=tr.querySelector('td.pub');var stc=(st&&(st.className.match(/st ?(\w+)?/)||[])[1])||'';var pc=PUBC[(pub?pub.textContent.trim():'')]||'';var parts=(cc?cc.textContent:'').split('/');var read=(parts[0]||'').trim().replace(/[^\d.,?]/g,''),lat=(parts[1]||'').replace(/[^\d.,?]/g,'');var cov=tr.dataset.cov;var img=cov?'<img data-src="'+escH(cov)+'" alt="">':'<div class=noimg>📚</div>';var nm=tileName(td);out.push('<div class=tile><a href="'+escH(a?a.href:'#')+'" target=_blank rel=noopener title="'+escH(nm)+'">'+img+'</a><div class=tchap><b class="st '+stc+'">'+escH(read||'0')+'</b><b class="tl '+pc+'">/'+escH(lat||'?')+'</b></div><div class=tname title="'+escH(nm)+'">'+escH(nm)+'</div></div>')});c.innerHTML=out.join('');
// EIGENES Lazy-Loading (natives loading=lazy laedt in eingebetteten/hintergruendigen Ansichten
// oft gar nicht): Bild-src erst setzen, wenn die Kachel in Sichtweite kommt (600px Vorlauf).
var tio=window.__tio;if(tio===undefined){tio=window.__tio=('IntersectionObserver' in window)?new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){var im=en.target;if(im.dataset.src){im.src=im.dataset.src;im.removeAttribute('data-src')}window.__tio.unobserve(im)}})},{rootMargin:'600px'}):null}
c.querySelectorAll('img[data-src]').forEach(function(im){if(tio)tio.observe(im);else{im.src=im.dataset.src;im.removeAttribute('data-src')}})}
// Kopf-Sortierleiste in der Kachelansicht EXAKT wie in der Tabelle (JB: 'gleiche Abstände'):
// ohne tbody verteilt der Browser die Spalten neu -> die Breiten werden mit SICHTBAREM tbody
// gemessen und als feste px eingefroren (table-layout:fixed; border-box, sonst kommt das
// Zellen-Padding obendrauf). WANN gemessen wird, ist entscheidend (JB-Fund: die Messung beim
// Seitenstart war zu frueh — die Schrift laedt nach und alle Breiten verschieben sich):
// refreezeHead() laeuft bei jedem buildTiles (Umschalten/Filtern/Sortieren), nach dem
// Font-Load und bei Fenster-Resize. Klasse kurz weg + wieder dran = kein sichtbares Flackern.
function freezeHead(){var t=document.getElementById('t');if(!t)return;var ths=t.querySelectorAll('thead th');var w=[...ths].map(function(th){return th.getBoundingClientRect().width});ths.forEach(function(th,i){th.style.boxSizing='border-box';th.style.width=w[i]+'px'});t.style.tableLayout='fixed'}
function unfreezeHead(){var t=document.getElementById('t');if(!t)return;t.style.tableLayout='';t.querySelectorAll('thead th').forEach(function(th){th.style.width='';th.style.boxSizing=''})}
function refreezeHead(){if(!document.body.classList.contains('tiles'))return;document.body.classList.remove('tiles');unfreezeHead();freezeHead();document.body.classList.add('tiles')}
window.addEventListener('resize',refreezeHead);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(refreezeHead);
function toggleTiles(){var on=document.body.classList.toggle('tiles');if(!on)unfreezeHead();try{localStorage.setItem('tiles',on?'1':'')}catch(e){}var b=document.getElementById('til');if(b)b.classList.toggle('on',on);if(on)buildTiles()}
function applyTiles(){if(localStorage.getItem('tiles')){document.body.classList.add('tiles');var b=document.getElementById('til');if(b)b.classList.add('on');buildTiles()}}

// --- Cover-Vorschau (JB): Hover ueber die Serien-Spalte laedt das Cover LAZY (data-cov der Zeile;
// kein HTML-Gewicht, kein Netz ohne Hover). Kurze Verzoegerung gegen Flackern beim Scrollen. ---
var covT;
document.addEventListener('mouseover',function(ev){var td=ev.target.closest&&ev.target.closest('#t tbody td:first-child');if(!td)return;var tr=td.closest('tr'),u=tr&&tr.dataset.cov;if(!u)return;clearTimeout(covT);covT=setTimeout(function(){var f=document.getElementById('covfly');if(!f){f=document.createElement('div');f.id='covfly';f.innerHTML='<img alt="">';document.body.appendChild(f)}var img=f.querySelector('img');if(img.dataset.u!==u){img.src=u;img.dataset.u=u}var r=td.getBoundingClientRect();f.style.top=Math.max(8,Math.min(window.innerHeight-230,r.top-60))+'px';f.style.left=Math.min(window.innerWidth-170,r.left+Math.max(180,r.width-60))+'px';f.style.display='block'},160)});
document.addEventListener('mouseout',function(ev){if(ev.target.closest&&ev.target.closest('#t tbody td:first-child')){clearTimeout(covT);var f=document.getElementById('covfly');if(f)f.style.display='none'}});

// --- Fortschrittsbalken (JB): laedt data/sync_progress.js als <script> nach — Script-Tags sind
// von der file://-Sperre AUSGENOMMEN, der Balken funktioniert also auch bei doppelt geklickter
// Datei ohne Server. War die Liste noch LEER (Erstaufbau) und der Sync wird fertig, laedt die
// Seite sich von selbst neu -> aus dem Balken wird die fertige Liste. ---
// Nutzer-Aktivitaet merken: waehrend jemand liest/klickt wird NIE ausgetauscht (nur bei Ruhe).
var lastAct=Date.now();['mousedown','keydown','wheel','touchstart'].forEach(function(ev){document.addEventListener(ev,function(){lastAct=Date.now()},true)});
// --- DYNAMISCHES Nachladen (JB: 'nicht dynamisch hinzubekommen?'): neuer Render -> data/list_rows.js
// holen und NUR die Tabellen-Zeilen austauschen. Kein Seiten-Reload: Scroll, Filter, Theme bleiben.
// Ein harter Reload passiert nur noch EINMAL am Ende eines Erstaufbaus (fuer Genre-Chips & Zaehler). ---
var LTSseen=(typeof I!=='undefined'&&I.rts)||0,startedEmpty=null;
function refreshRows(){document.querySelectorAll('#t tbody tr').forEach(function(r){r.classList.toggle('fav',FAV.has(r.dataset.h))});var oc=cfmGet();document.querySelectorAll('#t tbody tr').forEach(function(tr){if(oc[tr.dataset.h]){var c=tr.querySelector('.cfm');if(c)c.classList.add('on')}});var a=brkGet(),nn={};a.forEach(function(x){nn[x.name]=1});document.querySelectorAll('#t tbody tr').forEach(function(tr){if(nn[tr.dataset.n]){var b=tr.querySelector('.rep');if(b){b.classList.add('on');b.textContent='⚠ ✓'}}});var w=document.querySelector('.welcome');if(w&&document.querySelectorAll('#t tbody tr').length>0)w.style.display='none';applyTips();applyChapFix();pinFavs(true);updateAb();updateFav();regray();ff()}
function loadRows(){var s=document.createElement('script');s.src='data/list_rows.js?_='+Date.now();s.onload=function(){try{s.remove()}catch(e){}try{if(typeof LROWS!=='undefined'&&window.LTS&&window.LTS>LTSseen){LTSseen=window.LTS;document.querySelector('#t tbody').innerHTML=LROWS;var sb=document.querySelector('.sub');if(sb&&window.LSUB)sb.textContent=LSUB;refreshRows()}}catch(e){}};s.onerror=function(){try{s.remove()}catch(e){}};document.head.appendChild(s)}
function updSync(d){var b=document.getElementById('syncbar');if(!b||!d)return;if(startedEmpty===null)startedEmpty=document.querySelectorAll('#t tbody tr').length===0;var age=Date.now()/1000-(d.ts||0),fresh=age<900;var offen=d.total>0&&d.done<d.total;
// laufend = Herzschlag juenger als 90s; sonst AUSGEGRAUT mit Hinweis (JB: 'Tray geschlossen —
// update paused') statt kommentarlos verschwinden. Der Quit-Stempel des Trays wirkt sofort,
// der Herzschlag-Check faengt auch harte Abstuerze. Nach 24h ohne Lebenszeichen ganz aus.
if(offen&&d.phase!=='pausiert'&&age<90){b.classList.remove('pau');b.style.display='block';var pc=Math.round(100*d.done/d.total);b.querySelector('.fill').style.width=pc+'%';document.getElementById('synctxt').textContent=((typeof I!=='undefined'&&I.sy)||'Aktualisiere')+': '+d.done+'/'+d.total+' ('+pc+'%)'}
else if(offen&&age<86400){b.classList.add('pau');b.style.display='block';var pc2=Math.round(100*d.done/d.total);b.querySelector('.fill').style.width=pc2+'%';document.getElementById('synctxt').textContent=((typeof I!=='undefined'&&I.syp)||'Update pausiert')+' — '+d.done+'/'+d.total+' ('+pc2+'%)'}
else{b.style.display='none';b.classList.remove('pau')}
var stamp=Math.max(d.rendered||0,(d.total>0&&d.done>=d.total&&fresh)?(d.ts||0):0);
if(!(stamp>LTSseen&&fresh))return;
var empty=document.querySelectorAll('#t tbody tr').length===0;
if(!(empty||Date.now()-lastAct>10000))return;
if(startedEmpty&&d.total>0&&d.done>=d.total&&stamp*1000>performance.timeOrigin){location.reload();return}
loadRows()}
function pollSync(){try{var s=document.createElement('script');s.src='data/sync_progress.js?_='+Date.now();s.onload=function(){try{s.remove()}catch(e){}updSync(window.SYNCP)};s.onerror=function(){try{s.remove()}catch(e){}};document.head.appendChild(s)}catch(e){}setTimeout(pollSync,5000)}

// --- Empfehlungen neu mischen (JB): aus dem eingebetteten Pool (RECSPOOL, bis 30) 12 zufaellige ziehen ---
function escH(x){return String(x).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
function shuffleRecs(){try{var g=document.getElementById('recsgrid');if(!g||typeof RECSPOOL==='undefined')return;var p=RECSPOOL.slice();for(var i=p.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=p[i];p[i]=p[j];p[j]=t}g.innerHTML=p.slice(0,12).map(function(r){var rd=r.r?('<a class=rgo href="'+escH(r.r)+'" target=_blank rel=noopener title="'+((typeof I!=='undefined'&&I.rgo)||'Kapitel 1 lesen')+'">📖</a>'):'';return '<span class=rwrap><a class=stile href="'+escH(r.u)+'" target=_blank rel=noopener title="'+escH(r.g)+'">'+escH(r.t)+' <b>⭐'+escH(r.s)+'</b></a>'+rd+'</span>'}).join('')}catch(e){}}

// --- Titel-Bestaetigung (JB): unsichere Matches per ✔ als korrekt markieren -> Export title_confirms.json
// -> tools/apply_confirms.py pinnt sie fest (mb_id-Override). Gespeichert in localStorage 'titleCfm'.
function cfmGet(){try{return JSON.parse(localStorage.getItem('titleCfm')||'{}')}catch(e){return{}}}
function cfmSave(o){localStorage.setItem('titleCfm',JSON.stringify(o));var b=document.getElementById('cfb'),n=Object.keys(o).length;if(b){b.textContent='✔ '+n;b.style.display=n?'':'none'}}
function cfm(el){var tr=el.closest('tr'),k=tr.dataset.h,o=cfmGet();if(o[k]){delete o[k];el.classList.remove('on')}else{o[k]=1;el.classList.add('on')}cfmSave(o)}
function showCfm(){var o=cfmGet();if(!Object.keys(o).length)return;var b=new Blob([JSON.stringify(o,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),el=document.createElement('a');el.href=u;el.download='title_confirms.json';el.click();URL.revokeObjectURL(u)}
(function(){var o=cfmGet();cfmSave(o);document.querySelectorAll('#t tbody tr').forEach(function(tr){if(o[tr.dataset.h]){var c=tr.querySelector('.cfm');if(c)c.classList.add('on')}})})();

// --- "Link kaputt"-Melden: pro Serie merken (localStorage 'brk'), Export als broken_links.json ---
function brkGet(){try{return JSON.parse(localStorage.getItem('brk')||'[]')}catch(e){return[]}}
function brkSave(a){localStorage.setItem('brk',JSON.stringify(a));var b=document.getElementById('rb');if(b){b.textContent='🛠 '+a.length;b.style.display=a.length?'':'none'}}
// (JB Runde 40: das automatische Aufklappen von +Alt nach einer Meldung ist raus — melden
// soll melden, nicht das Menue oeffnen.)
function rep(btn){var tr=btn.closest('tr'),name=tr.dataset.n||'',a=brkGet(),i=a.findIndex(function(x){return x.name===name});if(i>=0){a.splice(i,1);brkSave(a);btn.classList.remove('on');btn.textContent='⚠'}else{var link=tr.querySelector('.pill.go'),url=link?link.href:'';a.push({name:name,url:url,ts:Date.now()});brkSave(a);btn.classList.add('on');btn.textContent='⚠✓'}}
// 🛠 Wartung (JB Runde 38, Feature 2): Meldungen ZUERST direkt an den Tray-Server uebergeben
// (127.0.0.1:8765/broken -> Manga/data/broken_links.json, der naechste Sync repariert von
// selbst). Laeuft das Tray nicht (exe-Nutzer/anderer PC), Fallback = Datei-Download wie bisher.
function showBrk(){var a=brkGet();if(!a.length)return;
var dl=function(){var b=new Blob([JSON.stringify(a,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),el=document.createElement('a');el.href=u;el.download='broken_links.json';el.click();URL.revokeObjectURL(u)};
if(typeof fetch==='undefined'){dl();return}
var ctl=(typeof AbortController!=='undefined')?new AbortController():null;if(ctl)setTimeout(function(){ctl.abort()},2500);
fetch('http://127.0.0.1:8765/broken',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(a),signal:ctl?ctl.signal:undefined})
.then(function(r){if(!r.ok)throw 0;return r.json()})
.then(function(){brkSave([]);document.querySelectorAll('button.rep.on').forEach(function(b){b.classList.remove('on');b.textContent='⚠'});alert((typeof I!=='undefined'&&I.brkSent)||'🛠 An die Reparatur übergeben — der nächste Sync prüft die Serien komplett neu.')})
.catch(function(){dl()})}
// beim Laden bereits gemeldete Zeilen (aus localStorage) wieder markieren
(function(){var a=brkGet();brkSave(a);var n={};a.forEach(function(x){n[x.name]=1});document.querySelectorAll('#t tbody tr').forEach(function(tr){if(n[tr.dataset.n]){var b=tr.querySelector('.rep');if(b){b.classList.add('on');b.textContent='⚠ ✓'}}})})();

// +Alt-Akkordeon: oeffnet man ein Alternativen-Menue, schliessen sich die anderen (Aesthetik).
document.addEventListener('toggle',function(e){var d=e.target;if(d.tagName==='DETAILS'&&d.classList.contains('alt')&&d.open){document.querySelectorAll('details.alt[open]').forEach(function(o){if(o!==d)o.open=false})}},true);

// --- Boot: Favoriten markieren + initial (ungelesen>Bewertung) nach oben pinnen; Checkbox/Zaehler; dann Filter ---
document.querySelectorAll('#t tbody tr').forEach(function(r){r.classList.toggle('fav',FAV.has(r.dataset.h))});
// Tooltips + Such-Links einmalig verteilen (HTML-Diaet: Texte/Domain-Liste stehen in I.tt statt
// x-fach je Zeile im HTML; die Google-URLs baut das Boot aus data-n/data-rc + der sq-Domain-Liste)
function applyTips(){try{var T=(typeof I!=='undefined'&&I.tt)||null;if(!T)return;var G='https://www.google.com/search?q=';document.querySelectorAll('#t tbody tr').forEach(function(tr){var q=function(sel){return tr.querySelector(sel)};var m={'.arch':T.arch,'.unarch':T.unarch,'.favi':T.fav,'td.c':T.c,'.rep':T.rep,'.cfm':T.cfm,'.gsr':T.galt};for(var sel in m){var el=q(sel);if(el&&m[sel])el.title=m[sel]}var st=q('td.st');if(st){var cls=(st.className.match(/st ?(\w+)?/)||[])[1]||'';st.title=T.st[cls]||T.st['']||''}var n=tr.dataset.n||'',rc=tr.dataset.rc||'';
// JB-Swap: 'suchen' (Aktion) = KOMBI-Suche ueber die Lese-Seiten (site:-Filter); +Alt = normale Google-Suche.
var s1=q('a.gsr');if(s1)s1.href=G+encodeURIComponent(n+' chapter '+rc+' ('+(T.sq||'')+')');var s2=q('a.galt');if(s2)s2.href=G+encodeURIComponent(n+' manga online chapter '+rc)})}catch(e){}}
// --- ⬆ nach-oben (JB): kleiner Pfeil unten rechts, sichtbar ab 600px Scrolltiefe ---
(function(){var b=document.createElement('button');b.id='top';b.textContent='⬆';b.title=(typeof I!=='undefined'&&I.tp)||'Nach oben';b.onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};document.body.appendChild(b);addEventListener('scroll',function(){b.style.display=scrollY>600?'block':'none'},{passive:true})})();
// Einmalige Bereinigung (JB 05.07.2026): alte, dotlose Pause-Schluessel (z.B. bare 'mangafire'
// aus dem temporaeren Umbau-Notbehelf) klemmten die Pause fest, weil togglePause heute
// Hostnamen schreibt. Solche Reste entfernen; echte Nutzer-Pausen (Hostnamen mit '.') bleiben.
function migratePauses(){try{var ov=pausedGet(),ch=false;Object.keys(ov).forEach(function(k){if(k.indexOf('.')<0){delete ov[k];ch=true}});if(ch)localStorage.setItem('pausedReaders',JSON.stringify(ov))}catch(e){}}
migratePauses();
// Dropdown-Akkordeon (JB 05.07.2026): Statistik / Empfehlungen / +Spalten / ⏸ Pausen + Genre-
// Filter klappen als OVERLAY unter dem Button auf (CSS position:absolute) -> die Button-/Filter-
// Reihe bleibt stehen, kein Zeilenumbruch. Nur EINES offen; oeffnet man das naechste, schliesst
// das vorherige; ein Klick ausserhalb schliesst ebenfalls (JB: 'auf ein anderes Feld -> klappt ein').
function panelAccordion(){var ps=document.querySelectorAll('.panels>details, details.genres');
[].forEach.call(ps,function(d){d.addEventListener('toggle',function(){
  if(d.open){[].forEach.call(ps,function(o){if(o!==d&&o.open)o.open=false});}});});
document.addEventListener('click',function(ev){
  [].forEach.call(ps,function(d){if(d.open&&!d.contains(ev.target))d.open=false;});});}
panelAccordion();
applyTheme();applyTips();applyChapFix();applyDense();pinFavs(true);updateAb();updateFav();regray();ff();applyTiles();applyPause();pollSync();
