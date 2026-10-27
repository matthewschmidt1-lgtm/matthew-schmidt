import json, re
j=json.load(open('tools/pina/egg.json')); svg=j['svg']; samples=j['samples']
# --- slim the markup: shared attributes become classes
svg=svg.replace(' stroke="#1E2021" stroke-width="0.9" stroke-linejoin="round" opacity="0.97"',' class="r"')
svg=svg.replace(' stroke="#1E2021" stroke-width="0.7" stroke-linejoin="round" opacity="0.93"',' class="i"')
svg=svg.replace(' stroke="#1E2021" stroke-width="1.7" stroke-linejoin="round"',' class="o"')
svg=svg.replace(' stroke="#1E2021" stroke-width="1.3" stroke-linejoin="round"',' class="f"')
svg=svg.replace(' stroke="#1E2021" stroke-width="1.1" stroke-linecap="round" opacity="0.35"',' class="g"')
svg=svg.replace(' stroke="#1E2021" stroke-width="0.9" opacity="0.35" stroke-linecap="round"',' class="l"')
svg=svg.replace(' stroke="#8E7A44" stroke-width="0.9" opacity="0.5" stroke-linecap="round"',' class="b"')
svg=re.sub(r'(\d)\.0\b', r'\1', svg)              # 380.0 -> 380
svg=re.sub(r'rgb\((\d+),(\d+),(\d+)\)', lambda m:'#%02x%02x%02x'%tuple(int(x) for x in m.groups()), svg)
style='<style>.r{stroke:#1E2021;stroke-width:.9;stroke-linejoin:round;opacity:.97}.i{stroke:#1E2021;stroke-width:.7;stroke-linejoin:round;opacity:.93}.o{stroke:#1E2021;stroke-width:1.7;stroke-linejoin:round}.f{stroke:#1E2021;stroke-width:1.3;stroke-linejoin:round}.g{stroke:#1E2021;stroke-width:1.1;stroke-linecap:round;opacity:.35}.l{stroke:#1E2021;stroke-width:.9;opacity:.35;stroke-linecap:round}.b{stroke:#8E7A44;stroke-width:.9;opacity:.5;stroke-linecap:round}</style>'
# --- timeline (18s loop): closed until .37, open by .50, hold, snap back at .851 while the frame is hidden
D='dur="18s" repeatCount="indefinite"'
def anim(attr, vals, keys, extra=''):
    return '<animate attributeName="%s" values="%s" keyTimes="%s" %s %s/>' % (attr, ';'.join(vals), ';'.join(keys), D, extra)
# ground and the piece shadows appear as it opens; the closed shadow gives way
def inject(pattern, add, count=1):
    global svg
    svg, n = re.subn(pattern, lambda m: m.group(0)+add, svg); assert n==count, (pattern, n)
inject(r'<g opacity="0" data-ground="1"[^>]*>', anim('opacity',['0','0','1','1','0','0'],['0','.40','.50','.85','.851','1']))
inject(r'<ellipse[^>]*data-closed-shadow="1"[^>]*>', anim('opacity',['1','1','.12','.12','1','1'],['0','.37','.50','.85','.851','1']))
inject(r'<g data-whole="1"[^>]*>', anim('opacity',['1','1','0','0','1','1'],['0','.37','.375','.85','.851','1']))
svg=svg.replace('<g data-shadow="1">','<g data-shadow="1" opacity="0">')
inject(r'<g data-shadow="1" opacity="0">', anim('opacity',['0','0','1','1','0','0'],['0','.37','.46','.85','.851','1']), 4)
# the four pieces: sampled translate + rotate from the store's easing, spread over .37 -> .50
keys=['0','.37','.396','.422','.448','.474','.50','.85','.851','1']
for q in (2,3,1,0):
    smp=[next(p for p in s if p['q']==q) for s in samples]   # 6 samples e=0..1
    closed=smp[0]; seq=[closed,closed]+smp[1:]+[smp[-1],closed,closed]
    tr=';'.join('%g %g'%(p['tx'],p['ty']) for p in seq)
    ro=';'.join('%g %g %g'%(p['rot'],p['cx'],p['cy']) for p in seq)
    a=('<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" %s/>'
       '<animateTransform attributeName="transform" type="rotate" additive="sum" values="%s" keyTimes="%s" %s/>') % (tr,';'.join(keys),D,ro,';'.join(keys),D)
    tag='<g data-piece="%d"><g transform="translate(380 305)">'%q
    assert svg.count(tag)==1, tag
    svg=svg.replace(tag, tag+a)
out='<svg xmlns="http://www.w3.org/2000/svg" class="codigo-scene" viewBox="60 90 640 470" aria-hidden="true">'+style+svg+'</svg>'
open('images/codigo/pina.svg','w').write(out)
print('pina.svg bytes', len(out))
