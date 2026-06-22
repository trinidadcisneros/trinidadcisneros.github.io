import re, json, sys
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from itree_specs import SPECS
from itree_content import CODE, EX
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

def cap(x): return x[:1].upper()+x[1:] if x else x

def leaf_node(title, desc, anchor):
    n={'leaf':title,'desc':desc,'anchor':anchor}
    if anchor in CODE: n['code']=CODE[anchor]
    if anchor in EX:
        ic,ir,oc,orr=EX[anchor]
        n['inCols'],n['inRows'],n['outCols'],n['outRows']=ic,ir,oc,orr
    return n

def to_tree(steps):
    def node(i):
        st=steps[i]; opts=[]
        for b in st['branches']:
            if 'leaf' in b:
                t,sub,anc=b['leaf']
                ln=leaf_node(t,sub,anc)
                o={'label':cap(b['label']),'cap':sub,'next':ln}
                if anc in EX:
                    oc,orr=EX[anc][2],EX[anc][3]
                    o['preview']={'cols':oc,'rows':orr[:2]}
                opts.append(o)
            else:
                opts.append({'label':cap(b['label']),'next':node(i+1)})
        q=st['q']; q=' '.join(q) if isinstance(q,(list,tuple)) else q
        n={'q':q,'options':opts}
        if st.get('sub'): n['sub']=st['sub']
        return n
    return node(0)

# ---- gl tree: rich hand-authored example data ----
def C(t,v): return {'t':t,'v':v}
glTree={
 'q':"Should users who DON'T qualify still appear in the result?",
 'sub':"Example: bob is active only 3 days; the gate is 5 days. Compare the two outputs.",
 'options':[
  {'label':"No — leave non-qualifiers out completely",'cap':"bob disappears entirely",
   'ex':{'cols':["user","active","min_calories"],'rows':[["alice","6","180"],[C('gone','bob'),C('gone','3'),C('gone','—')],["eve","5","150"]]},
   'next':leaf_node("WHERE filter","A plain WHERE drops non-qualifiers — they never reach the output.","gl-leaf-where")},
  {'label':"Yes — keep them, blank as NaN / NULL",'cap':"bob stays, with NaN  ← your problem needs this",
   'ex':{'cols':["user","active","min_calories"],'rows':[["alice","6","180"],["bob","3",C('nan','NaN')],["eve","5","150"]]},
   'next':{
     'q':"Do you need OTHER columns from the winning row, or just the one number (the min / max)?",
     'sub':"Just the min calories, or also which workout it was?",
     'options':[
       {'label':"Just the one number (min calories)",'cap':"one value per user",
        'ex':{'cols':["user","min_calories"],'rows':[["alice","180"],["bob",C('nan','NaN')]]},
        'next':{
          'q':"Where does the gate live — on the entity, or on the fact rows you're aggregating?",
          'sub':"Active days is a fact about the user; price > 75 is a fact about each row.",
          'options':[
            {'label':"On the entity (a flag, status, or threshold about the user)",'cap':"wrap the aggregate in a CASE → CASE around the aggregate",
             'ex':{'cols':["user","min_calories"],'rows':[["alice","180"],["bob",C('nan','NaN')]]},
             'next':{
               'q':"Is that entity gate a number comparison, or a yes/no flag / status value?",
               'sub':"score >= 70   vs   is_active = true / status = 'active'.",
               'options':[
                 {'label':"A number comparison (score >= 70, rate >= 80)",'cap':"numeric threshold gate",
                  'ex':{'cols':["user","min_calories"],'rows':[["alice","180"],["bob",C('nan','NaN')]]},
                  'next':leaf_node("Numeric threshold gate","Wrap MIN/MAX in CASE WHEN a.col >= n THEN agg END; the entity still appears, blank as NULL / 0 when the number misses.","gl-case-around-threshold")},
                 {'label':"A yes/no flag or a status value",'cap':"boolean / status flag gate",
                  'ex':{'cols':["user","min_calories"],'rows':[["alice","180"],["bob",C('nan','NaN')]]},
                  'next':leaf_node("Boolean / status flag gate","Same wrap, gate is a.is_verified / a.status = 'active'; NULL / 0 when the flag is off.","gl-case-around-flag")}
               ]}},
            {'label':"On the fact rows (only some rows qualify, e.g. price > 75)",'cap':"keep every entity, count only the qualifying rows",
             'ex':{'cols':["user","valid_workouts"],'rows':[["alice","1"],["bob","0"]]},
             'next':{
               'q':"Keep every entity and count only the qualifying rows — which form?",
               'sub':"Both keep all entities via LEFT JOIN and land non-matchers on 0.",
               'options':[
                 {'label':"Filter in the JOIN ON, then COUNT the survivors",'cap':"filter in ON, then COUNT(b.id)",
                  'ex':{'cols':["user","valid_workouts"],'rows':[["alice","1"],["bob","0"]]},
                  'next':leaf_node("Gate in the JOIN ON","Put the row filter in LEFT JOIN … ON so only qualifying rows attach; COUNT(b.id) gives 0 for none.","gl-leaf-onclause")},
                 {'label':"Sum a CASE inside the aggregate",'cap':"SUM(CASE WHEN cond THEN 1 ELSE 0)",
                  'ex':{'cols':["user","valid_workouts"],'rows':[["alice","1"],["bob","0"]]},
                  'next':leaf_node("CASE inside the aggregate","SUM/COUNT(CASE WHEN b.cond THEN 1 ELSE 0 END) counts only qualifying rows; LEFT JOIN makes non-matching entities 0. Same result as filtering in the JOIN ON.","gl-case-inside")}
               ]}}
          ]}},
       {'label':"Other columns too (e.g. the workout name)",'cap':"carry the winning row's other fields",
        'ex':{'cols':["user","min_calories",C('extra','workout_name')],'rows':[["alice","180",C('extra','Yoga')],["bob",C('nan','NaN'),C('extra','NULL')]]},
        'next':{
          'q':"Does it need to run on any database, or is Postgres-only fine?",
          'options':[
            {'label':"Any database",'cap':"portable: ROW_NUMBER, keep rn = 1",
             'ex':{'cols':["user","min_calories",C('extra','workout')],'rows':[["alice","180",C('extra','Yoga')],["bob",C('nan','NaN'),C('extra','NULL')]]},
             'next':leaf_node("ROW_NUMBER + rn = 1","Number each user's workouts (cheapest = 1), keep rn = 1 — that row carries the name too.","gl-leaf-rownumber")},
            {'label':"Postgres is fine",'cap':"shortcut: DISTINCT ON",
             'ex':{'cols':["user","workout","cal"],'rows':[["alice","Yoga","180"]]},
             'next':leaf_node("DISTINCT ON","Postgres DISTINCT ON (user) … ORDER BY user, cal keeps the top row per user in one line.","gl-leaf-distincton")}
          ]}}
     ]}}
 ]}

ALLTREES={'gl-itree':glTree}
for did,steps in SPECS.items():
    ALLTREES[did+'-itree']=to_tree(steps)

# ---- code-and-example-aware renderer ----
RENDER=r'''function itreeTable(cols, rows){
  function cell(c){
    if(c && typeof c==='object'){
      if(c.t==='nan')  return '<td class="ix-nan">'+c.v+'</td>';
      if(c.t==='gone') return '<td class="ix-gone">'+c.v+'</td>';
      if(c.t==='extra')return '<td class="ix-extra">'+c.v+'</td>';
      return '<td>'+c.v+'</td>';
    }
    if(c==='NaN'||c==='NULL') return '<td class="ix-nan">'+c+'</td>';
    return '<td>'+c+'</td>';
  }
  var h='<table class="ix"><tr>'+cols.map(function(c){return '<th>'+c+'</th>';}).join('')+'</tr>';
  rows.forEach(function(r){ h+='<tr>'+r.map(cell).join('')+'</tr>'; });
  return h+'</table>';
}
function renderITree(id, tree){
  var root=document.getElementById(id); if(!root) return; var path=[];
  function node(){ return path.length? path[path.length-1].node : tree; }
  function draw(){
    root.innerHTML='';
    path.forEach(function(p){ var c=document.createElement('div'); c.className='itree-crumb'; c.innerHTML='<b>'+p.q+'</b> &rarr; '+p.choice; root.appendChild(c); });
    var n=node();
    if(n.leaf){
      var d=document.createElement('div'); d.className='itree-leaf';
      var html='<div class="itree-leaf-title">&#10003; Use: '+n.leaf+'</div><div class="itree-leaf-desc">'+n.desc+'</div>';
      if(n.code){ html+='<div class="itree-lbl">Generic template</div><pre class="itree-code"><code>'+n.code.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</code></pre>'; }
      if(n.inCols){ html+='<div class="itree-lbl">Worked example</div><div class="itree-exwrap">'+itreeTable(n.inCols,n.inRows)+'<div class="itree-arrow">&darr; run the query &darr;</div>'+itreeTable(n.outCols,n.outRows)+'</div>'; }
      if(n.anchor){ html+='<a class="itree-recipe" href="#'+n.anchor+'">Open the full recipe &rarr;</a>'; }
      d.innerHTML=html; root.appendChild(d);
    } else {
      var q=document.createElement('div'); q.className='itree-q'; q.textContent=n.q; root.appendChild(q);
      if(n.sub){ var sb=document.createElement('div'); sb.className='itree-subq'; sb.textContent=n.sub; root.appendChild(sb); }
      var opts=document.createElement('div'); opts.className='itree-opts';
      n.options.forEach(function(o){
        var b=document.createElement('div'); b.className='itree-opt';
        var inner='<div class="itree-opt-label">'+o.label+'</div>';
        if(o.cap) inner+='<div class="itree-opt-cap">'+o.cap+'</div>';
        if(o.ex) inner+=itreeTable(o.ex.cols,o.ex.rows);
        else if(o.preview) inner+=itreeTable(o.preview.cols,o.preview.rows);
        b.innerHTML=inner;
        b.onclick=function(){ path.push({q:n.q, choice:o.label, node:o.next}); draw(); };
        opts.appendChild(b);
      });
      root.appendChild(opts);
    }
    if(path.length){ var bk=document.createElement('button'); bk.type='button'; bk.className='itree-reset'; bk.style.marginRight='16px'; bk.textContent='← Back one step'; bk.onclick=function(){ path.pop(); draw(); }; root.appendChild(bk); var r=document.createElement('button'); r.type='button'; r.className='itree-reset'; r.textContent='Start over'; r.onclick=function(){ path=[]; draw(); }; root.appendChild(r); }
  }
  draw();
}'''

CSS='''
    /* ---- interactive tree: example data ---- */
    .itree-subq{font-size:0.92rem;color:#64748b;margin:-4px 0 10px;}
    .itree-opt{text-align:left;padding:12px 14px;border:1px solid #cbd5e1;border-radius:10px;background:#f8fafc;cursor:pointer;margin-bottom:11px;}
    .itree-opt:hover{border-color:#1565c0;background:#eef4fb;}
    .itree-opt-label{font-size:1.0rem;font-weight:700;color:#1e293b;}
    .itree-opt-cap{font-size:0.85rem;color:#64748b;margin:3px 0 8px;}
    table.ix{border-collapse:collapse;font-size:0.8rem;margin-top:4px;}
    table.ix th{background:#1e293b;color:#fff;padding:4px 9px;text-align:left;font-weight:600;border:1px solid #334155;white-space:nowrap;}
    table.ix td{padding:4px 9px;border:1px solid #cbd5e1;color:#1e293b;background:#fff;white-space:nowrap;}
    td.ix-nan{background:#fff3e0;color:#b45309;font-weight:700;}
    td.ix-gone{background:#fee2e2;color:#b91c1c;text-decoration:line-through;}
    td.ix-extra{background:#e8f5e9;color:#166534;font-weight:600;}
    .itree-lbl{font-size:0.82rem;font-weight:700;color:#475569;margin:12px 0 4px;}
    .itree-exwrap{display:flex;flex-direction:column;gap:2px;align-items:flex-start;}
    .itree-arrow{font-size:0.82rem;color:#64748b;margin:4px 0;}
    .itree-recipe{display:inline-block;margin-top:12px;color:#1565c0;font-weight:600;text-decoration:none;}
'''

text=open(PATH).read()

# 1) add example CSS once
if 'table.ix{' not in text:
    i=text.find('</style>'); text=text[:i]+CSS+text[i:]

# 2) remove the existing consolidated script (function renderITree ... )
text=re.sub(r'<script>\s*function (itreeTable|renderITree).*?</script>\s*', '', text, flags=re.S)
text=re.sub(r'<script>\s*var COWORK_ITREES.*?</script>\s*', '', text, flags=re.S)

# 3) one consolidated script before </body>
data=json.dumps(ALLTREES, ensure_ascii=False)
assert '</script>' not in data
js='<script>\n'+RENDER+'\nvar COWORK_ITREES='+data+';\n'
js+="document.addEventListener('DOMContentLoaded',function(){for(var k in COWORK_ITREES){renderITree(k,COWORK_ITREES[k]);}});\n</script>\n"
b=text.rfind('</body>'); text=text[:b]+js+text[b:]

# balance
do=len(re.findall(r'<div\b',text)); dc=len(re.findall(r'</div\b',text))
d=0;mn=0
for m in re.finditer(r'<(/?)div\b',text):
    d+=1 if m.group(1)=='' else -1; mn=min(mn,d)
assert do==dc and d==0 and mn>=0 and text.count('<svg')==text.count('</svg>'), (do,dc,d,mn)
assert text.count('function renderITree')==1
open(PATH,'w').write(text)
ex_ct=sum(1 for k in EX); leaf_ct=sum(1 for t in SPECS.values() for st in t for b in st['branches'] if 'leaf' in b)
print('OK trees',len(ALLTREES),'| leaves',leaf_ct,'| examples',ex_ct,'| div',do,dc)
