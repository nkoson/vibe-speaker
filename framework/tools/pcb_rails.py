#!/usr/bin/env python3
"""Describe a shared-rail prototype PCB, export its resistive wiring and drawings.

Geometry and connectivity diagnostics are quantities, not design verdicts.
All coordinates are millimetres viewed from the copper/component side.
"""
import argparse, copy, csv, json, math
from pathlib import Path


def distance(a,b): return math.dist(a,b)
def on_segment(p,a,b,tol=1e-6): return abs(distance(a,p)+distance(p,b)-distance(a,b))<tol
def length(points): return sum(distance(a,b) for a,b in zip(points,points[1:]))
def point_segment(p,a,b):
    d=[b[i]-a[i] for i in range(2)]; q=sum(x*x for x in d)
    t=max(0,min(1,sum((p[i]-a[i])*d[i] for i in range(2))/q)) if q else 0
    return distance(p,[a[i]+t*d[i] for i in range(2)])
def segment_distance(a,b,c,d):
    def cross(u,v,w):return (v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0])
    if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:return 0.
    return min(point_segment(a,c,d),point_segment(b,c,d),point_segment(c,a,b),point_segment(d,a,b))

def compile_layout(layout, circuit):
    out=copy.deepcopy(circuit);out['wires']=[]
    rho=layout.get('rho_ohm_mm2_m',.0175); contact=layout.get('lead_contact_ohm',.0005)
    rows=[]; taps={}; rails={}; aliases={}; components={c['id']:c for c in out['components']}
    reports={'rail_clearances_mm':[],'hole_to_copper_clearances_mm':[], 'body_clearances_mm':[], 'component_node_mismatches':[], 'disconnected_logical_nodes':[], 'rail_length_mm':0,'lead_length_mm':0,'hole_pair_clearances_mm':[],'mount_to_lead_plan_clearances_mm':[]}
    parent={}
    def root(n):
        parent.setdefault(n,n)
        if parent[n]!=n:parent[n]=root(parent[n])
        return parent[n]
    def join(a,b):parent[root(a)]=root(b)
    def wire(id,a,b,mm,area,kind,extra=0):
        r=rho*mm/1000/area+extra
        out['wires'].append({'id':id,'from':a,'to':b,'resistance_ohm':r})
        rows.append({'id':id,'from':a,'to':b,'length_mm':round(mm,3),'section_mm2':area,'contact_ohm':extra,'resistance_ohm':r,'kind':kind});join(a,b)
    def tap(bid,rid,p):
        key=(bid,rid); point=tuple(float(x) for x in p)
        if key not in rails:raise ValueError(f'Unknown rail {key}')
        if not any(on_segment(point,a,b) for a,b in zip(rails[key]['points'],rails[key]['points'][1:])):raise ValueError(f'Tap {point} outside {key}')
        taps.setdefault(key,{})[point]=f'{bid}.{rid}.{point[0]:g}.{point[1]:g}'
        return taps[key][point]
    for b in layout['boards']:
        for r in b['rails']:rails[b['id'],r['id']]=r
    for b in layout['boards']:
        bid=b['id']
        for name,(rid,p) in b['terminals'].items():aliases[f'{bid}:{name}']=tap(bid,rid,p)
        for c in b['parts']:
            if c['id'] not in components:raise ValueError(f"Missing circuit body {c['id']}")
            target=layout['logical_components'][c['id']]
            for i,lead in enumerate(c['leads']):
                r=rails[bid,lead['rail']]
                if r['net']!=target[i]:reports['component_node_mismatches'].append([c['id'],i,r['net'],target[i]])
                node=tap(bid,lead['rail'],lead['points'][-1]);mm=length(lead['points'])+c.get('stand_off_mm',0)
                wire(c['id']+'-lead-'+str(i+1),components[c['id']]['nodes'][i],node,mm,layout.get('lead_section_mm2',.5),'native_lead',contact)
                reports['lead_length_mm']+=mm
        for j in b.get('jumpers',[]):
            a=tap(bid,*j['a']);z=tap(bid,*j['b']);wire(j['id'],a,z,j['length_mm'],layout.get('link_section_mm2',1.5),'insulated_board_jumper',2*contact)
        rr=b['rails']
        for i,r in enumerate(rr):
            for s in rr[i+1:]:
                if r['net']==s['net']:continue
                gap=min(segment_distance(a,z,c,d) for a,z in zip(r['points'],r['points'][1:]) for c,d in zip(s['points'],s['points'][1:]))-(r['width_mm']+s['width_mm'])/2
                reports['rail_clearances_mm'].append({'board':bid,'rails':[r['id'],s['id']],'gap_mm':gap})
        holes=[('mount',p,2.5) for p in b['holes']]+[(c['id'],p,c.get('restraint_hole_diameter_mm',3.5)/2) for c in b['parts'] for p in c['restraint_holes_mm']]
        for i,(hid,p,radius) in enumerate(holes):
            for other,q,r2 in holes[i+1:]:
                reports['hole_pair_clearances_mm'].append({'board':bid,'holes':[hid,other],'points':[p,q],'edge_gap_mm':distance(p,q)-radius-r2})
        for p in b['holes']:
            for part in b['parts']:
                for i,lead in enumerate(part['leads']):
                    gap=min(point_segment(p,a,z) for a,z in zip(lead['points'],lead['points'][1:]))-2.5
                    reports['mount_to_lead_plan_clearances_mm'].append({'board':bid,'point':p,'component':part['id'],'lead':i+1,'centreline_to_hole_edge_mm':gap})
        for hid,p,radius in holes:
            gap=min(point_segment(p,a,z)-r['width_mm']/2-radius for r in rr for a,z in zip(r['points'],r['points'][1:]))
            reports['hole_to_copper_clearances_mm'].append({'board':bid,'id':hid,'point':p,'gap_mm':gap})
        for i,c in enumerate(b['parts']):
            for d in b['parts'][i+1:]:
                dx=abs(c['x']-d['x'])-(c['body_w']+d['body_w'])/2;dy=abs(c['y']-d['y'])-(c['body_h']+d['body_h'])/2
                gap=math.hypot(max(dx,0),max(dy,0)) if max(dx,dy)>=0 else max(dx,dy)
                reports['body_clearances_mm'].append({'board':bid,'parts':[c['id'],d['id']],'bounding_box_gap_mm':gap})
    for h in layout['harness']:
        wire(h['id'],aliases.get(h['from'],h['from']),aliases.get(h['to'],h['to']),h['length_mm'],layout.get('link_section_mm2',1.5),'harness',2*contact)
    for (bid,rid),r in rails.items():
        for p in r['points']:tap(bid,rid,p)
        for k,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
            points=sorted([p for p in taps[bid,rid] if on_segment(p,a,b)],key=lambda p:distance(a,p))
            for j,(p,q) in enumerate(zip(points,points[1:])):
                mm=distance(p,q); path_length=length(r['points']); electrical_mm=mm*r.get('cut_length_mm',path_length)/path_length; wire(f'{bid}-{rid}-{k}-{j}',taps[bid,rid][p],taps[bid,rid][q],electrical_mm,r['section_mm2'],'rail');reports['rail_length_mm']+=mm
    groups={}
    for c in out['components']:
        for node,net in zip(c['nodes'],layout['logical_components'][c['id']]):groups.setdefault(net,set()).add(root(node))
    for net,roots in groups.items():
        if len(roots)!=1:reports['disconnected_logical_nodes'].append({'net':net,'groups':sorted(roots)})
    netroots={net:roots for net,roots in groups.items()};reports['shorted_logical_nodes']=[[a,b] for i,a in enumerate(netroots) for b in list(netroots)[i+1:] if netroots[a]&netroots[b]]
    reports['counts']={kind:sum(r['kind']==kind for r in rows) for kind in {r['kind'] for r in rows}}
    reports['counts'].update(boards=len(layout['boards']),components=len(components),rail_paths=len(rails),straight_rail_pieces=sum(len(r['points'])-1 for r in rails.values()))
    reports['substrate_volume_l']=sum(b['size_mm'][0]*b['size_mm'][1]*b['size_mm'][2] for b in layout['boards'])/1e6
    reports['rail_volume_l']=sum(length(r['points'])*r['section_mm2'] for r in rails.values())/1e6
    return out,rows,reports


def draw(layout,path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import mm
    c=canvas.Canvas(str(path),pagesize=(594*mm,420*mm));c.setTitle(layout['title'])
    def text(x,y,s,size=9):c.setFont('Helvetica',size);c.drawString(x*mm,y*mm,str(s))
    def wrap(x,y,s,width=83):
        import textwrap
        for line in textwrap.wrap(s,width):text(x,y,line);y-=5
        return y-3
    def page(title,code):
        c.setFillColor(HexColor('#16364b'));c.rect(0,401*mm,594*mm,19*mm,fill=1,stroke=0);c.setFillColor(HexColor('#ffffff'));text(12,408,title,16);c.setFillColor(HexColor('#111111'));text(12,9,f'{code} | Revision {layout["revision"]} | All dimensions mm | copper/component side unless labelled');text(470,9,layout.get('drawing_label','Crossover PCB'),10)
    for b in layout['boards']:
        for physical in [False,True]:
            page(f'{b["id"]} - '+('components, leads and restraints' if physical else 'shared copper rails and isolation'),b['id']+('-P' if physical else '-C'))
            ox,oy=15,30
            def line(points,color,width=1,dash=None):
                c.setStrokeColor(HexColor(color));c.setLineWidth(width*mm);c.setDash(dash or [])
                path=c.beginPath();path.moveTo((ox+points[0][0])*mm,(oy+points[0][1])*mm)
                for point in points[1:]:path.lineTo((ox+point[0])*mm,(oy+point[1])*mm)
                c.drawPath(path)
                c.setDash([])
            c.setLineWidth(.4*mm);c.setStrokeColor(HexColor('#222222'));c.rect(ox*mm,oy*mm,b['size_mm'][0]*mm,b['size_mm'][1]*mm)
            for r in b['rails']:
                line(r['points'],'#b87333',5)
                p=r['points'][0];c.setFillColor(HexColor('#111111'));text(ox+p[0]+3,oy+p[1]+3,f'{r["id"]}: {r["net"]}',8)
            for p in b['holes']:
                c.setStrokeColor(HexColor('#111111'));c.setLineWidth(.25*mm);c.circle((ox+p[0])*mm,(oy+p[1])*mm,2.5*mm);c.circle((ox+p[0])*mm,(oy+p[1])*mm,5*mm)
            if physical:
                for v in b['parts']:
                    x,y,w,h=v['x'],v['y'],v['body_w'],v['body_h'];c.setFillColor(HexColor('#edf2f5'));c.setStrokeColor(HexColor('#365b70'));c.setLineWidth(.3*mm)
                    if v['type']=='L' and v['axis']=='Z':c.circle((ox+x)*mm,(oy+y)*mm,w/2*mm,fill=1)
                    else:c.roundRect((ox+x-w/2)*mm,(oy+y-h/2)*mm,w*mm,h*mm,2*mm,fill=1)
                    c.setFillColor(HexColor('#111111'));text(ox+x-w/2+2,oy+y,v['id']+(f' axis {v["axis"]}' if v['axis'] else ''),10)
                    for lead in v['leads']:line(lead['points'],'#30343b',.55)
                    for p in v['restraint_holes_mm']:
                        c.setStrokeColor(HexColor('#7d3754'));c.setLineWidth(.25*mm);c.circle((ox+p[0])*mm,(oy+p[1])*mm,1.75*mm)
                for j in b.get('jumpers',[]):line(j['path'],'#247aa4',.75,[3,2]);p=j['path'][1];text(ox+p[0]+1,oy+p[1]+2,j['id'],8)
            text(15,16,f'1:1 at A2. Datum (0,0): bottom-left. {b["size_mm"][0]} x {b["size_mm"][1]} board.',10)
            y=390
            if physical:
                y=wrap(250,y,'Body centres / envelopes / endpoint rails A then B',65)
                for v in b['parts']:
                    text(250,y,f'{v["id"]}: ({v["x"]:g}, {v["y"]:g})  {v["body_w"]:g} x {v["body_h"]:g}  |  {v["leads"][0]["rail"]} / {v["leads"][1]["rail"]}',10);y-=5
                y-=4;y=wrap(250,y,'3.5 mm restraint holes (violet). Coordinates:',35)
                for v in b['parts']:text(250,y,v['id']+': '+' / '.join(f'{p[0]:g},{p[1]:g}' for p in v['restraint_holes_mm']),8);y-=5
                y=wrap(250,y-3,'Fit coils/capacitors on 3 mm resilient pads. Resistors: 15 mm ceramic supports and glass-fibre lacing. Two nylon ties per coil; do not use a metal loop. Copper is below the bodies; sleeve any lead crossing another node.',35)
            else:
                y=wrap(250,y,'Rail centreline coordinates, in sequence. 1 x 5 mm copper strip. Use mitred butt joints soldered over an isolated copper land; maintain 5 mm finished width.',35)
                for r in b['rails']:
                    y=wrap(250,y,f'{r["id"]} = {r["net"]}: '+ ' > '.join(f'({p[0]:g},{p[1]:g})' for p in r['points']),38)
                y=wrap(250,y,b.get('copper_preparation','Remove copper outside the rail footprints; bridge isolated lands with the specified strip.'),65)
            text(250,75,'Mounting: D5 holes; clear copper to D10. Insulating washers and stand-offs.',9)
            wrap(250,69,'Mount centres: '+' / '.join(f'{x:g},{y:g}' for x,y in b['holes']),80)
            text(250,48,'Restraint holes D3.5 through; deburr both faces. See installation sheet for lacing.',9)
            c.showPage()
    page('PCB installation and harness',f'P{2*len(layout["boards"])+1}')
    y=390
    notes=layout.get("installation_notes", [])
    for i,n in enumerate(notes,1):y=wrap(15,y,f'{i}. {n}',155)
    c.showPage();page('Harness and rail connections',f'P{2*len(layout["boards"])+2}');y=390
    text(15,y,'ID     From                         To                         Cut length / conductor',12);y-=12
    for h in layout['harness']:
        text(15,y,h['id']);text(40,y,h['from']);text(120,y,h['to']);text(205,y,f'{h["length_mm"]} mm / 1.5 mm2');y-=8
    y-=10;y=wrap(15,y,'Terminal locations, local PCB coordinates. These labels identify common rails, not extra isolated screw terminals.',145)
    for b in layout['boards']:
        for net,(rid,p) in b['terminals'].items():text(15,y,f'{b["id"]}:{net} = rail {rid}, ({p[0]:g},{p[1]:g})');y-=6
    y-=8;wrap(15,y,layout.get('harness_notes',''),145)
    c.showPage();c.save()


def export_cad(layout, folder):
    """Millimetre board/copper/holes DXFs and 1:1 copper artwork SVGs."""
    import ezdxf
    from xml.sax.saxutils import escape
    folder.mkdir(parents=True, exist_ok=True)
    for b in layout['boards']:
        doc=ezdxf.new('R2010');doc.units=4;doc.header['$INSUNITS']=4;ms=doc.modelspace()
        for layer in ['BOARD','COPPER','MOUNT','RESTRAINT','DIM']:doc.layers.new(layer)
        w,h,t=b['size_mm'];ms.add_lwpolyline([(0,0),(w,0),(w,h),(0,h)],close=True,dxfattribs={'layer':'BOARD'})
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}"><title>{escape(b["id"])} copper artwork; component side</title><rect width="{w}" height="{h}" fill="white"/><g transform="translate(0,{h}) scale(1,-1)" fill="none" stroke="black" stroke-linejoin="miter" stroke-linecap="butt">']
        for r in b['rails']:
            ms.add_lwpolyline(r['points'],dxfattribs={'layer':'COPPER','const_width':r['width_mm']})
            points=' '.join(f'{x},{y}' for x,y in r['points']);svg.append(f'<polyline points="{points}" stroke-width="{r["width_mm"]}"/>')
        for point in b['holes']:ms.add_circle(point,2.5,dxfattribs={'layer':'MOUNT'})
        for part in b['parts']:
            for point in part['restraint_holes_mm']:ms.add_circle(point,1.75,dxfattribs={'layer':'RESTRAINT'})
        for p1,p2,base,angle in [((0,0),(w,0),(0,-12),0),((0,0),(0,h),(-12,0),90)]:
            dim=ms.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,dimstyle='EZDXF',override={'dimtxt':3,'dimasz':2.5},dxfattribs={'layer':'DIM'});dim.render()
        name=folder/f'PCB-{b["id"]}.dxf';doc.saveas(name);reopened=ezdxf.readfile(name)
        if reopened.units!=4 or reopened.audit().has_errors:raise ValueError(f'DXF round-trip: {name}')
        svg.append('</g></svg>');(folder/f'PCB-{b["id"]}-copper.svg').write_text('\n'.join(svg)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--circuit',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--pdf',type=Path);a=ap.parse_args()
    layout=json.loads(a.input.read_text());circuit=json.loads(a.circuit.read_text());board,rows,audit=compile_layout(layout,circuit);a.out.mkdir(parents=True,exist_ok=True)
    for name,obj in [('pcb-board.params.json',board),('pcb-audit.json',audit)]: (a.out/name).write_text(json.dumps(obj,indent=2)+'\n')
    with (a.out/'pcb-conductors.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    export_cad(layout,a.out/'pcb-cad')
    if a.pdf:draw(layout,a.pdf)
    print(json.dumps({'counts':audit['counts'],'node_mismatches':audit['component_node_mismatches'],'disconnected':audit['disconnected_logical_nodes'],'shorted':audit['shorted_logical_nodes']}))
if __name__=='__main__':main()
