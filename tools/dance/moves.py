"""Regenerates the dnIvory / dnEbony keyframes in index.html (The Dance card).

Sixteen alternating moves, eight per pawn, each a lift-and-land hop; the gaps and hop
lengths shrink geometrically so the game speeds up. Run from the site root:
    python3 tools/dance/moves.py
"""
p='index.html'; s=open(p,encoding='utf-8').read()
T=20.0
ivory=[(-6,-8,.9),(-2,-14,.84),(-9,-18,.78),(-13,-21,.73),(-10,-25,.68),(-16,-28,.63),(-19,-30,.59),(-23,-33,.55)]
ebony=[(-5,-8,.9),(-11,-11,.85),(-8,-16,.79),(-14,-20,.74),(-18,-23,.69),(-15,-27,.64),(-21,-30,.6),(-25,-33,.56)]
t=1.5; moves=[]
for k in range(16):
    dur=0.7*(0.93**k); moves.append((k%2, t, t+dur)); t+=dur+1.1*(0.82**k)
end_moves=t
def kf(name, path, who):
    pos=[(0,0,1.0)]+path; lines=[]
    pct=lambda x: f"{100*x/T:.2f}%"
    tf=lambda x,y,sc: f"transform:translate({x}%,{y}%) scale({sc});"
    mine=[m for m in moves if m[0]==who]
    lines.append(f"    0%,{pct(mine[0][1])}{{ {tf(*pos[0])} opacity:1; animation-timing-function:ease-in-out; }}")
    for i,(w,a,b) in enumerate(mine):
        x0,y0,s0=pos[i]; x1,y1,s1=pos[i+1]; hop=3.5*s1
        lines.append(f"    {pct((a+b)/2)}{{ {tf(round((x0+x1)/2,1), round((y0+y1)/2-hop,1), round((s0+s1)/2,3))} animation-timing-function:ease-in-out; }}")
        nxt = mine[i+1][1] if i+1<len(mine) else end_moves+0.3
        lines.append(f"    {pct(b)},{pct(nxt)}{{ {tf(x1,y1,s1)} opacity:1; animation-timing-function:{'ease-in-out' if i+1<len(mine) else 'ease-in'}; }}")
    x,y,sc=pos[-1]
    lines.append(f"    {pct(end_moves+1.8)},{pct(T-2.0)}{{ {tf(x-8,y-8,round(sc*.8,3))} opacity:0; }}")
    lines.append(f"    {pct(T-1.9)}{{ {tf(0,0,1.0)} opacity:0; animation-timing-function:ease-out; }}")
    lines.append(f"    {pct(T-0.7)},100%{{ {tf(0,0,1.0)} opacity:1; }}")
    return f"  @keyframes {name}{{\n"+"\n".join(lines)+"\n  }\n"
i=s.index('  @keyframes dnIvory{'); j=s.index('  .dance-cap{')
s=s[:i]+kf('dnIvory',ivory,0)+kf('dnEbony',ebony,1)+s[j:]
open(p,'w',encoding='utf-8').write(s); print('keyframes written; moves end at %.2fs of %.0fs'%(end_moves,T))
