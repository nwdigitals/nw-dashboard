import re, shutil, os
D='/home/user/dash'
s=open(f'{D}/original.html',encoding='utf-8').read()

def rep(old,new,count=1):
    global s
    assert old in s, 'NOT FOUND: '+old[:80]
    s=s.replace(old,new,count)

# ── 0. split off original script block (everything from 2nd <script> after </tbody>) ──
body_end=s.find('</tbody>')
js_start=s.find('<script>',body_end)
js_orig=s[js_start:]
html=s[:js_start]
s=html

# ── 1. head: fix dead inline code inside the gun <script src>, add storage shim for sandboxed previews ──
g0=s.find('<script src="https://cdn.jsdelivr.net/npm/gun/gun.js">')
g1=s.find('</script>',g0)+len('</script>')
s=s[:g0]+'''<script>
/* Storage shim: if the browser blocks localStorage (private/sandboxed frames) fall back to memory so the app still runs. */
(function(){try{localStorage.getItem('_t')}catch(e){var m={};var sh={getItem:function(k){return Object.prototype.hasOwnProperty.call(m,k)?m[k]:null},setItem:function(k,v){m[k]=String(v)},removeItem:function(k){delete m[k]},clear:function(){m={}},key:function(i){return Object.keys(m)[i]||null},get length(){return Object.keys(m).length}};try{Object.defineProperty(window,'localStorage',{value:sh,configurable:true})}catch(e2){}}})();
</script>
<script src="https://cdn.jsdelivr.net/npm/gun/gun.js"></script>'''+s[g1:]

# ── 2. CSS additions ──
css_add = r'''
  /* ═══ PIPELINE v2 additions (same palette, same components) ═══ */
  .pipeline{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;padding:12px 16px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.015)}
  .stage{position:relative;text-align:left;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;cursor:pointer;color:var(--text);font-family:inherit;display:grid;grid-template-columns:auto 1fr auto;grid-template-areas:"n t c" "h h h";gap:2px 8px;align-items:center;min-width:0;transition:.15s}
  .stage:hover{border-color:var(--line2);background:#15264A}
  .stage.active{border-color:var(--lime);box-shadow:0 0 0 1px var(--lime-glow) inset,0 4px 14px var(--lime-glow)}
  .stage:not(:last-child)::after{content:"›";position:absolute;right:-9px;top:50%;transform:translateY(-52%);color:var(--dim);font-size:16px;font-weight:900;z-index:1;pointer-events:none}
  .stage .sn{grid-area:n;width:22px;height:22px;border-radius:50%;background:rgba(132,204,22,.14);border:1px solid rgba(132,204,22,.3);color:var(--lime);font-size:11px;font-weight:900;display:flex;align-items:center;justify-content:center}
  .stage.active .sn{background:var(--lime);color:#0A1225}
  .stage .st{grid-area:t;font-size:11px;font-weight:900;letter-spacing:.03em;text-transform:uppercase;overflow-wrap:anywhere}
  .stage .sc{grid-area:c;font-size:16px;font-weight:900;color:var(--text)}
  .stage .sh{grid-area:h;font-size:10px;color:var(--muted);font-weight:600;line-height:1.35;margin-top:4px}
  .stage.close{cursor:default}
  .stage.close:hover{background:var(--card);border-color:var(--line)}
  .stage.close.active{border-color:var(--lime)}
  .stage .sh-close{display:flex;gap:5px;flex-wrap:wrap}
  .mini{font-family:inherit;font-size:9px;font-weight:900;letter-spacing:.05em;padding:3px 7px;border-radius:999px;border:1px solid var(--line2);background:#0A1430;color:var(--muted);cursor:pointer}
  .mini.won{color:#86EFAC;border-color:rgba(134,239,172,.3)} .mini.lost{color:#FCA5A5;border-color:rgba(239,68,68,.3)}
  .mini.on{background:var(--text);color:var(--bg);border-color:var(--text)}
  .status-select.status-new{color:#CBD5E1}
  .status-select.status-perm{color:#7DD3FC;border-color:rgba(56,189,248,.35);background:rgba(56,189,248,.08)}
  .status-select.status-call{color:#FDE68A;border-color:rgba(245,158,11,.4);background:rgba(245,158,11,.10)}
  .status-select.status-prop{color:#D9F99D;border-color:rgba(132,204,22,.4);background:rgba(132,204,22,.08)}
  .status-select.status-won{color:#0A1225;background:var(--lime);border-color:var(--lime)}
  .status-select.status-lost{color:#FCA5A5;border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.10)}
  .status-select.status-arch{color:var(--dim);border-style:dashed}
  .leak-chip{font-size:11px;background:rgba(245,158,11,.12);color:#FDE68A;border:1px solid rgba(245,158,11,.22);padding:2px 7px;border-radius:6px;display:inline-block;overflow-wrap:anywhere;word-break:break-word;max-width:200px}
  .rev-input{width:78px;padding:5px 7px;border:1px solid var(--line);border-radius:8px;background:#0A1430;color:var(--text);font-size:11px;max-width:100%}
  .card-input{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:9px;background:#060D1F;color:var(--text);font-size:12px;max-width:100%}
  .empty-pipe{padding:44px 20px;text-align:center;color:var(--muted);background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0}
  td > .empty-pipe{border:none;border-radius:0;background:var(--card2)}
  .empty-pipe .ep-title{font-weight:900;color:var(--text);margin-top:8px;font-size:14px}
  .empty-pipe .ep-sub{font-size:12px;margin-top:6px;line-height:1.6;max-width:520px;margin-left:auto;margin-right:auto}
  .lib-key{background:var(--lime);color:#0A1225;padding:2px 6px;border-radius:6px;font-size:10px;white-space:nowrap}
  .lib-step{background:rgba(255,255,255,.07);color:var(--muted);padding:2px 6px;border-radius:6px;font-size:10px;white-space:nowrap;font-weight:800}
  .agenda{margin:8px 0 0 18px;font-size:12px;color:var(--muted);line-height:1.7}
  .agenda b{color:var(--text)}
  .agenda-rule{margin-top:10px;font-size:11px;color:#FDE68A;background:rgba(245,158,11,.10);border:1px solid rgba(245,158,11,.25);padding:9px;border-radius:8px;line-height:1.5}
  .funnel{margin:0 16px 16px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
  .funnel h4{font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
  .fn-row{display:grid;grid-template-columns:170px 1fr 120px;gap:12px;align-items:center;padding:6px 0}
  .fn-label{font-size:12px;font-weight:800}
  .fn-bar{height:10px;background:#0A1430;border:1px solid var(--line);border-radius:999px;overflow:hidden}
  .fn-bar span{display:block;height:100%;background:linear-gradient(90deg,var(--lime2),var(--lime));border-radius:999px;min-width:0}
  .fn-num{text-align:right;line-height:1.1} .fn-num b{font-size:16px;font-weight:900} .fn-num small{display:block;font-size:10px;color:var(--dim);margin-top:2px}
  .fn-foot{margin-top:8px;font-size:11px;color:var(--dim);line-height:1.5}
  @media(max-width:900px){.pipeline{display:flex;overflow-x:auto;scrollbar-width:none;padding:10px 12px}.pipeline::-webkit-scrollbar{display:none}.stage{min-width:178px;flex-shrink:0}.stage:not(:last-child)::after{display:none}}
  @media(max-width:640px){.fn-row{grid-template-columns:1fr 90px;grid-template-areas:"l n" "b b"}.fn-label{grid-area:l}.fn-num{grid-area:n}.fn-bar{grid-area:b}.funnel{margin:0 10px 12px}}
</style>
</head>'''
rep('</style>\n</head>', css_add)

# ── 3. header / stats ──
rep('<div class="stat-sub">Top work-now targets</div>','<div class="stat-sub">Open leads to work first</div>')
rep('<div class="stat lime"><div class="stat-label">Audits Sent</div><div class="stat-value" id="statAudits">0</div><div class="stat-sub">Status ≥ Audit Sent</div></div>',
    '<div class="stat lime"><div class="stat-label">Calls Booked</div><div class="stat-value" id="statBooked">0</div><div class="stat-sub">Reached Call Scheduled</div></div>')
rep('<div class="stat-sub">Status = Proposal Sent</div></div>\n  <div class="stat lime"><div class="stat-label">Deals WON</div>','<div class="stat-sub">Reached Proposal Sent</div></div>\n  <div class="stat lime"><div class="stat-label">Deals WON</div>')
rep('<div class="stat-sub" id="statWonSub">0% close rate</div>','<div class="stat-sub" id="statWonSub">0% of proposals • 0 lost</div>')

# ── 4. Leads panel ──
rep('<h3 id="leadCommandTitle">LEAD COMMAND — RANKED 1→100 <em>TAP WHATSAPP TO CHAT</em></h3>','<h3 id="leadCommandTitle">LEAD COMMAND — 0 IN PIPELINE <em>TAP WHATSAPP TO CHAT</em></h3>')
rep('<option value="NURTURE">NURTURE only</option>','<option value="NURTURE">NURTURE only</option>')
rep('<option value="all">All Status</option><option>New Lead</option><option>Permission Asked</option><option>Audit Sent</option><option>Proposal Sent</option><option>WON</option><option>LOST</option>',
    '<option value="all">All Status</option><option>New Lead</option><option>Permission Asked</option><option>Call Scheduled</option><option>Proposal Sent</option><option>WON</option><option>LOST</option><option>Archive</option>')
rep('<a class="btn-sm" href="ranked-1-100.pdf" target="_blank" rel="noopener" style="text-decoration:none">Original PDF</a>\n','')
rep('<div class="swipe-hint">','<div class="pipeline" id="pipeline" aria-label="Sales pipeline"></div>\n    <div class="swipe-hint">')
rep('💡 Click Status to update. Next Date auto-sorts Follow-Up Queue.','💡 Move each lead one step at a time — Status sets the next action and date. Next Date sorts the Follow-Up Queue.')

# ── 5. Daily panel ──
rep('<div class="form-group"><label>Audits Sent</label><input type="number" id="dailyAudits" placeholder="0" min="0"></div>\n','')
rep('<div class="form-group"><label>Looms Recorded</label><input type="number" id="dailyLooms" placeholder="0" min="0"></div>\n','')
rep('<div class="form-group"><label>Calls Booked</label><input type="number" id="dailyCalls" placeholder="0" min="0"></div>',
    '<div class="form-group"><label>Calls Booked</label><input type="number" id="dailyCalls" placeholder="0" min="0"></div>\n        <div class="form-group"><label>Calls Held</label><input type="number" id="dailyHeld" placeholder="0" min="0"></div>')
rep('<th>Date</th><th>Asks</th><th>Audits</th><th>Replies</th><th>Calls</th><th>Props</th><th>Deals</th><th>Revenue</th><th></th>',
    '<th>Date</th><th>Asks</th><th>Replies</th><th>Booked</th><th>Held</th><th>Props</th><th>Deals</th><th>Revenue</th><th></th>')

# ── 6. Metrics panel ──
mA=s.find('<div class="metrics-grid">'); mB=s.find('</div>\n    <div style="margin:0 16px 16px 16px;background:rgba(245,158,11,.08)',mA)
new_metrics='''<div class="metrics-grid">
      <div class="metric-card"><h4>Total Leads</h4><div class="value" id="mTotal">0</div><div class="sub">In pipeline</div></div>
      <div class="metric-card"><h4>Permission Asks Sent</h4><div class="value" id="mAsks">0</div><div class="sub">From Daily Activity</div></div>
      <div class="metric-card"><h4>Replies</h4><div class="value" id="mReplies">0</div><div class="sub" id="mReplyRate">0% reply rate</div></div>
      <div class="metric-card"><h4>Calls Scheduled</h4><div class="value" id="mBooked">0</div><div class="sub">Leads that reached Step 3</div></div>
      <div class="metric-card"><h4>Calls Held</h4><div class="value" id="mHeld">0</div><div class="sub">From Daily Activity</div></div>
      <div class="metric-card"><h4>Proposals Sent</h4><div class="value" id="mProps">0</div><div class="sub">Leads that reached Step 4</div></div>
      <div class="metric-card"><h4>Deals WON</h4><div class="value" id="mDeals" style="color:#86EFAC">0</div><div class="sub" id="mCloseRate">0% close rate</div></div>
      <div class="metric-card"><h4>Total Revenue</h4><div class="value" id="mRevenue" style="color:#86EFAC">R0</div><div class="sub" id="mAvg">Avg R0</div></div>
    '''
s=s[:mA]+new_metrics+s[mB:]
rep('<div style="margin:0 16px 16px 16px;background:rgba(245,158,11,.08)','<div class="funnel"><h4>Pipeline conversion — 5 steps</h4><div id="funnel"></div></div>\n    <div style="margin:0 16px 16px 16px;background:rgba(245,158,11,.08)')
rep('<h3>METRICS DASHBOARD — Formula-Driven <em>AUTO FROM LEADS + DAILY</em></h3>','<h3>METRICS DASHBOARD — Formula-Driven <em>AUTO FROM LEADS + DAILY</em></h3>')

# ── 7. Library header ──
rep('<h3>QUICK REPLIES & VOICE NOTES — Autopilot Pack <em>TYPE / IN WHATSAPP BUSINESS</em></h3>','<h3>QUICK REPLIES &amp; CALL SCRIPT — Mapped to the 5 steps <em>TYPE / IN WHATSAPP BUSINESS</em></h3>')

# ── 8. Add-lead modal ──
rep('<option>HOT</option><option>WARM</option><option>COLD</option>','<option>HOT</option><option>WARM</option><option>NURTURE</option>')
rep('<div class="field"><label>Business Name *</label><input id="nlBusiness" placeholder="e.g. Rustenburg Paving Pros"></div>',
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div class="field"><label>Business Name *</label><input id="nlBusiness" placeholder="e.g. Rustenburg Paving Pros"></div><div class="field"><label>Contact person</label><input id="nlContact" placeholder="First name (for the greeting)"></div></div>')
rep('<div class="field"><label>1-Line Leak</label><input id="nlLeak" placeholder="e.g. No website, no WhatsApp on mobile"></div>',
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div class="field"><label>Website</label><input id="nlWebsite" placeholder="leave blank if none"></div><div class="field"><label>1-Line Leak</label><input id="nlLeak" placeholder="e.g. No WhatsApp button on mobile"></div></div>')
rep('<input id="nlNextAction" value="Permission ask">','<input id="nlNextAction" value="Send permission ask">')
rep('<h3>➕ New Lead</h3>','<h3>➕ New Lead <span style="font-size:10px;color:var(--lime);font-weight:800;margin-left:6px">STEP 1</span></h3>')

# ── 9. Script: new core + original FAB / PIN / sync with sync-apply hooks patched ──
core=open(f'{D}/app_core.js',encoding='utf-8').read()
fab=js_orig.find('// Draggable FAB')
assert fab>0
tail=js_orig[fab:]
n=tail.count('leads=obj.leads; daily=obj.daily;')
assert n==2, n
tail=tail.replace('leads=obj.leads; daily=obj.daily;','leads=normalizeLeads(obj.leads); daily=normalizeDaily(obj.daily);')
old_st="try{ const nl=JSON.parse(localStorage.getItem('nw_leads')||'[]'); if(Array.isArray(nl)) leads=nl; }catch(e){}"
assert old_st in tail
tail=tail.replace(old_st,"try{ const nl=JSON.parse(localStorage.getItem('nw_leads')||'[]'); if(Array.isArray(nl)) leads=normalizeLeads(nl); }catch(e){}")
# nothing in the tail should still reference audit statuses
s=s+'<script>\n'+core+'\n'+tail

# ── 10. title / manifest / sw unchanged; sw cache bump handled separately ──
open('/home/user/index.html','w',encoding='utf-8').write(s)
for f in ('logo.png','icon-192.png','icon-512.png','manifest.json'):
    shutil.copy(f'{D}/{f}',f'/home/user/{f}')
sw=open(f'{D}/sw.js').read()
sw=sw.replace("nw-command-v3-ranked100","nw-command-v5-perf").replace(", './ranked-1-100.pdf'","")
open('/home/user/sw.js','w').write(sw)
print('built', len(s), 'bytes')
