#!/usr/bin/env python3
"""Export component-led, shared-wire crossover assemblies and routing quantities."""
import argparse, csv, json, math
from pathlib import Path
from pcb_rails import compile_layout, length, distance, point_segment, segment_distance, on_segment


def route_metrics(layout):
    report={'boards':[], 'connected_pairs':[]}
    for board in layout['boards']:
        paths=board['rails'];parts=board['parts'];active_paths=[r for r in paths if r.get('kind')!='direct_joint']
        record={'id':board['id'],'body_count':len(parts),'node_wire_count':len(active_paths),'direct_joint_count':len(paths)-len(active_paths),'node_wire_path_mm':sum(length(r['points']) for r in paths),'cut_wire_mm':sum(r.get('cut_length_mm',length(r['points'])) for r in paths),'straight_runs':sum(len(r['points'])-1 for r in active_paths),'bends':sum(max(0,len(r['points'])-2) for r in active_paths),'native_lead_plan_mm':sum(length(l['points']) for c in parts for l in c['leads']),'separate_jumpers':len(board.get('jumpers',[]))}
        record['straight_runs']+=sum(len(j.get('path',[]))-1 for j in board.get('jumpers',[]) if j.get('path'))
        record['bends']+=sum(max(0,len(j.get('path',[]))-2) for j in board.get('jumpers',[]))
        record['native_lead_route_mm']=sum(l.get('length_mm',length(l['points'])+c.get('stand_off_mm',0)) for c in parts for l in c['leads'])
        record['internal_conductor_path_mm']=record['node_wire_path_mm']+record['native_lead_route_mm']+sum(length(j['path']) if j.get('path') else j['length_mm'] for j in board.get('jumpers',[]))
        report['boards'].append(record)
        byrail={r['id']:r for r in paths}
        def station(points,p):
            sofar=0
            for a,b in zip(points,points[1:]):
                if on_segment(p,a,b):return sofar+distance(a,p)
                sofar+=distance(a,b)
            raise ValueError('lead endpoint outside wire')
        for i,a in enumerate(parts):
            for b in parts[i+1:]:
                for ia,la in enumerate(a['leads']):
                    for ib,lb in enumerate(b['leads']):
                        if la['rail']!=lb['rail']:continue
                        points=byrail[la['rail']]['points']
                        mm=length(la['points'])+abs(station(points,la['points'][-1])-station(points,lb['points'][-1]))+length(lb['points'])
                        report['connected_pairs'].append({'board':board['id'],'parts':[a['id'],b['id']],'endpoints':[ia+1,ib+1],'node':byrail[la['rail']]['net'],'plan_route_mm':mm})
    report['totals']={k:sum(b[k] for b in report['boards']) for k in ['node_wire_count','direct_joint_count','node_wire_path_mm','cut_wire_mm','straight_runs','bends','native_lead_plan_mm','native_lead_route_mm','separate_jumpers','internal_conductor_path_mm']}
    return report


def construction_geometry(layout):
    report={'holes':[],'body_pairs':[],'lead_wire_crossings':[]}
    for b in layout['boards']:
        holes=[('mount',p,2.5) for p in b['holes']]+[(c['id'],p,c.get('restraint_hole_diameter_mm',3.5)/2) for c in b['parts'] for p in c['restraint_holes_mm']]+[('wire-'+a['wire'],p,1.75) for a in b.get('wire_anchors',[]) for p in a['holes']]
        for i,(tag,p,r) in enumerate(holes):
            edge=min(p[0],p[1],b['size_mm'][0]-p[0],b['size_mm'][1]-p[1])-r
            nearest=min((distance(p,q)-r-s for j,(_,q,s) in enumerate(holes) if j!=i),default=math.inf)
            report['holes'].append({'board':b['id'],'id':tag,'point':p,'edge_ligament_mm':edge,'nearest_hole_ligament_mm':nearest})
        for i,c in enumerate(b['parts']):
            for d in b['parts'][i+1:]:
                dx=abs(c['x']-d['x'])-(c['body_w']+d['body_w'])/2;dy=abs(c['y']-d['y'])-(c['body_h']+d['body_h'])/2
                gap=math.hypot(max(dx,0),max(dy,0)) if max(dx,dy)>=0 else max(dx,dy)
                report['body_pairs'].append({'board':b['id'],'parts':[c['id'],d['id']],'box_gap_mm':gap})
        for part in b['parts']:
            for index,lead in enumerate(part['leads']):
                for wire in b['rails']:
                    if wire['id']==lead['rail']:continue
                    gap=min(segment_distance(a,z,c,d) for a,z in zip(lead['points'],lead['points'][1:]) for c,d in zip(wire['points'],wire['points'][1:]))
                    if gap<1e-6:report['lead_wire_crossings'].append({'board':b['id'],'part':part['id'],'lead':index+1,'wire':wire['id']})
    return report


def draw(layout,path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    c=canvas.Canvas(str(path),pagesize=(594*mm,420*mm));c.setTitle(layout['title'])
    def text(x,y,s,size=10):c.setFont('Helvetica',size);c.drawString(x*mm,y*mm,str(s))
    def wrap(x,y,s,width=90):
        import textwrap
        for line in textwrap.wrap(s,width):text(x,y,line);y-=5
        return y-3
    def page(title,code):
        c.setFillColor(HexColor('#17384a'));c.rect(0,402*mm,594*mm,18*mm,fill=1,stroke=0);c.setFillColor(HexColor('#ffffff'));text(12,408,title,16);c.setFillColor(HexColor('#111111'));text(12,7,f'{code} | Revision {layout["revision"]} | mm | 1:1 on A2 | Component-side view');text(470,7,layout.get('drawing_label','Crossover'))
    for board in layout['boards']:
        for wiring in [True,False]:
            page(board['id']+(' - component placement and shared wires' if wiring else ' - drilling and restraint coordinates'),board['id']+('-W' if wiring else '-D'))
            ox,oy=15,10
            def line(points,color='#28566d',width=.7):
                c.setStrokeColor(HexColor(color));c.setLineWidth(width*mm);p=c.beginPath();p.moveTo((ox+points[0][0])*mm,(oy+points[0][1])*mm)
                for x,y in points[1:]:p.lineTo((ox+x)*mm,(oy+y)*mm)
                c.drawPath(p)
            c.setStrokeColor(HexColor('#444444'));c.setLineWidth(.3*mm);c.rect(ox*mm,oy*mm,board['size_mm'][0]*mm,board['size_mm'][1]*mm)
            if wiring:
                for r in board['rails']:
                    line(r['points']);x,y=r.get('label_at',[r['points'][0][0]+2,r['points'][0][1]+3]);text(ox+x,oy+y,f'{r["id"]} / {r["net"]}',8)
            for p in board['holes']:
                c.setStrokeColor(HexColor('#333333'));c.setLineWidth(.25*mm);c.circle((ox+p[0])*mm,(oy+p[1])*mm,2.5*mm)
            for part in board['parts']:
                x,y,w,h=part['x'],part['y'],part['body_w'],part['body_h'];c.setFillColor(HexColor('#edf2f5'));c.setStrokeColor(HexColor('#486776'));c.setLineWidth(.3*mm)
                if part['type']=='L' and part['axis']=='Z':c.circle((ox+x)*mm,(oy+y)*mm,w/2*mm,fill=1)
                else:c.roundRect((ox+x-w/2)*mm,(oy+y-h/2)*mm,w*mm,h*mm,2*mm,fill=1)
                c.setFillColor(HexColor('#111111'));text(ox+x-w/2+2,oy+y,part['id']+(f' axis {part["axis"]}' if part['axis'] else ''),10)
                if wiring:
                    for lead in part['leads']:
                        line(lead['points'],'#222222',.5);px,py=lead['points'][-1];c.setFillColor(HexColor('#222222'));c.circle((ox+px)*mm,(oy+py)*mm,.9*mm,fill=1,stroke=0)
                else:
                    for px,py in part['restraint_holes_mm']:
                        c.setStrokeColor(HexColor('#873954'));c.circle((ox+px)*mm,(oy+py)*mm,part.get('restraint_hole_diameter_mm',3.5)/2*mm)
            if wiring:
                for over in board.get('overpasses',[]):
                    x,y=over['point'];c.setFillColor(HexColor('#ffffff'));c.circle((ox+x)*mm,(oy+y)*mm,2*mm,fill=1,stroke=0);c.setStrokeColor(HexColor('#222222'));c.setLineWidth(.5*mm);c.arc((ox+x-2)*mm,(oy+y-2)*mm,(ox+x+2)*mm,(oy+y+2)*mm,0,180)
            c.setFillColor(HexColor('#111111'))
            if wiring:
                for _,(_,point) in board['terminals'].items():
                    c.setStrokeColor(HexColor('#a06a33'));c.setLineWidth(.45*mm);c.rect((ox+point[0]-1.5)*mm,(oy+point[1]-1.5)*mm,3*mm,3*mm)
            for anchor in board.get('wire_anchors',[]):
                if wiring:
                    x,y=anchor['point'];c.setStrokeColor(HexColor('#a06a33'));c.setLineWidth(.4*mm);c.line((ox+x-2)*mm,(oy+y-2)*mm,(ox+x+2)*mm,(oy+y+2)*mm)
                else:
                    for x,y in anchor['holes']:c.setStrokeColor(HexColor('#a06a33'));c.circle((ox+x)*mm,(oy+y)*mm,1.75*mm)
            y=390
            if wiring:
                y=wrap(250,y,board.get('interpretation',''),98)
                y=wrap(250,y,'Part centre (x,y), body envelope and endpoint wire IDs (A / B):',95)
                for p in board['parts']:
                    text(250,y,f'{p["id"]}: ({p["x"]:g}, {p["y"]:g})  {p["body_w"]:g} x {p["body_h"]:g}  |  {p["leads"][0]["rail"]} / {p["leads"][1]["rail"]}',10);y-=5
                y=wrap(250,y-3,'Shared-wire routes: coordinates describe the straight runs. Form rounded corners in the clear spaces; cut lengths include fitting allowance.',95)
                for r in board['rails']:y=wrap(250,y,f'{r["id"]} ({r["net"]}), cut {r["cut_length_mm"]:g} mm: '+' > '.join(f'{x:g},{z:g}' for x,z in r['points']),100)
                for over in board.get('overpasses',[]):y=wrap(250,y,over['instruction'],95)
                wrap(250,y,'Blue lines: ordinary insulated1.5 mm2 wire. Black dots: solder junctions. Crossings without a dot remain insulated. Brown slashes: wire ties; brown squares: harness attachment points. Black short lines: formed component leads.',95)
            else:
                y=wrap(250,y,f'{board["stock"]}. Datum at bottom-left. Mounting holes D5 through; coil-restraint holes D5; other restraint and wire-tie holes D3.5 through. Deburr both faces.',95)
                y=wrap(250,y,'D5 mounts: '+' / '.join(f'{x:g},{z:g}' for x,z in board['holes']),95)
                y=wrap(250,y,'Body restraint holes (violet):',95)
                for p in board['parts']:text(250,y,p['id']+f' D{p.get("restraint_hole_diameter_mm",3.5):g}: '+' / '.join(f'{x:g},{z:g}' for x,z in p['restraint_holes_mm']),10);y-=5
                y=wrap(250,y-3,'Wire-tie hole pairs (brown), grouped by wire ID:',95)
                for a in board.get('wire_anchors',[]):text(250,y,a['wire']+': '+' / '.join(f'{x:g},{z:g}' for x,z in a['holes']),9);y-=5
                wrap(250,y-4,'Lace the wires at the marked pairs before tightening the component restraints. Keep solder junctions visible during inspection. Install each component with the pad or ceramic support shown on C16.',95)
            c.showPage()
    page('Crossover assembly and installation','W5');y=390
    for i,n in enumerate(layout.get('installation_notes',[]),1):y=wrap(15,y,f'{i}. {n}',155)
    c.showPage();page('Amplifier and driver harness','W6');y=390
    for h in layout['harness']:text(15,y,h['id']);text(40,y,h['from']);text(130,y,h['to']);text(225,y,f'{h["length_mm"]} mm / 1.5 mm2');y-=9
    y=wrap(15,y-12,'Wire attachment points in local carrier coordinates:',145)
    for b in layout['boards']:
        for name,(rid,p) in b['terminals'].items():text(15,y,f'{b["id"]}:{name} = wire {rid}, ({p[0]:g},{p[1]:g})');y-=6
    wrap(15,y-10,layout.get('harness_notes',''),145);c.showPage();c.save()


def export_dxf(layout,folder):
    import ezdxf
    folder.mkdir(parents=True,exist_ok=True)
    for b in layout['boards']:
        doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
        for name in ['CARRIER','WIRE_GUIDE','MOUNT','RESTRAINT','WIRE_TIES','DIM']:doc.layers.new(name)
        w,h,_=b['size_mm'];ms.add_lwpolyline([(0,0),(w,0),(w,h),(0,h)],close=True,dxfattribs={'layer':'CARRIER'})
        for r in b['rails']:ms.add_lwpolyline(r['points'],dxfattribs={'layer':'WIRE_GUIDE'})
        for p in b['holes']:ms.add_circle(p,2.5,dxfattribs={'layer':'MOUNT'})
        for c in b['parts']:
            for p in c['restraint_holes_mm']:ms.add_circle(p,c.get('restraint_hole_diameter_mm',3.5)/2,dxfattribs={'layer':'RESTRAINT'})
        for a in b.get('wire_anchors',[]):
            for p in a['holes']:ms.add_circle(p,1.75,dxfattribs={'layer':'WIRE_TIES'})
        for p1,p2,base,angle in [((0,0),(w,0),(0,-12),0),((0,0),(0,h),(-12,0),90)]:ms.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,override={'dimtxt':3,'dimasz':2.5},dxfattribs={'layer':'DIM'}).render()
        path=folder/f'{b["id"]}-carrier.dxf';doc.saveas(path)
        if ezdxf.readfile(path).audit().has_errors:raise ValueError('DXF interchange error')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--circuit',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--pdf',type=Path);ap.add_argument('--compare',type=Path);a=ap.parse_args()
    layout=json.loads(a.input.read_text());board,rows,audit=compile_layout(layout,json.loads(a.circuit.read_text()));metrics=route_metrics(layout);geometry=construction_geometry(layout)
    a.out.mkdir(parents=True,exist_ok=True)
    for name,data in [('assembly-board.params.json',board),('assembly-audit.json',audit),('assembly-routing.json',metrics),('assembly-geometry.json',geometry)]: (a.out/name).write_text(json.dumps(data,indent=2)+'\n')
    with (a.out/'assembly-conductors.csv').open('w') as f:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (a.out/'shared-wire-cut-list.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['board','wire','node','path_mm','cut_mm','section_mm2'])
        for b in layout['boards']:
            for r in b['rails']:
                if r.get('kind')!='direct_joint':writer.writerow([b['id'],r['id'],r['net'],length(r['points']),r['cut_length_mm'],r['section_mm2']])
    if a.compare:(a.out/'routing-comparison.json').write_text(json.dumps({'previous':route_metrics(json.loads(a.compare.read_text())),'current':metrics},indent=2)+'\n')
    export_dxf(layout,a.out/'assembly-cad')
    if a.pdf:draw(layout,a.pdf)
    print(json.dumps(metrics['totals']))
if __name__=='__main__':main()
