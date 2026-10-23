#!/usr/bin/env python3
"""Print true-scale drilling templates and mirrored underside wiring for carriers.

The JSON owns every hole and route. This exporter does not choose placements.
Coordinates are millimetres, viewed from the component face, bottom-left origin.
"""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def all_holes(board):
    return board['drill_holes']


def audit(layout):
    records=[]
    for b in layout['boards']:
        holes=all_holes(b); w,h,_=b['size_mm']
        ids=[x['id'] for x in holes]
        if len(set(ids))!=len(ids): raise ValueError('Duplicate hole identifiers')
        edge=min(min(x['center'][0],x['center'][1],w-x['center'][0],h-x['center'][1])-x['diameter']/2 for x in holes)
        pairs=[(math.dist(a['center'],z['center'])-(a['diameter']+z['diameter'])/2,a['id'],z['id']) for a,z in itertools.combinations(holes,2)]
        closest=min(pairs)
        if edge<1 or closest[0]<1: raise ValueError(f'{b["id"]}: insufficient ligament {edge}, {closest}')
        leads=[x for x in holes if x['kind']=='lead']
        if len(leads)!=2*len(b['parts']): raise ValueError('Each component needs two lead holes')
        records.append({'board':b['id'],'holes':len(holes),'lead_holes':len(leads),'minimum_edge_ligament_mm':edge,'closest_holes':closest,'diameter_counts':{str(d):sum(x['diameter']==d for x in holes) for d in sorted({x['diameter'] for x in holes})}})
    return records


def draw_board(c,b,ox,oy,mirror=False,wiring=False,labels=True):
    w,h,_=b['size_mm']
    def xy(p): return ((ox+(w-p[0] if mirror else p[0]))*mm,(oy+p[1])*mm)
    def poly(points,color,width,dash=None):
        c.setStrokeColorRGB(*color);c.setLineWidth(width*mm);c.setDash(dash or [])
        p=c.beginPath();p.moveTo(*xy(points[0]))
        for q in points[1:]:p.lineTo(*xy(q))
        c.drawPath(p);c.setDash([])
    c.setStrokeColorRGB(0,0,0);c.setLineWidth(.35*mm);c.rect(ox*mm,oy*mm,w*mm,h*mm)
    for part in b['parts']:
        c.setStrokeColorRGB(.74,.74,.74);c.setLineWidth(.18*mm)
        if mirror:c.setDash([2*mm,1*mm])
        x,y=part['x'],part['y'];bw,bh=part['body_w'],part['body_h']
        if part['type']=='L' and part['axis']=='Z':c.circle(*xy([x,y]),bw/2*mm)
        else:
            xx=ox+(w-x-bw/2 if mirror else x-bw/2)
            c.rect(xx*mm,(oy+y-bh/2)*mm,bw*mm,bh*mm)
        c.setDash([])
        if labels:
            c.setFillColorRGB(.25,.25,.25);c.setFont('Helvetica-Bold',10)
            c.drawCentredString(xy([x,y])[0],xy([x,y])[1],part['id']+(f' / {part["axis"]}' if part.get('axis') else ''))
    if wiring:
        for r in b['rails']:
            poly(r['points'],(.05,.27,.45),.6)
            if labels:
                x,y=r.get('label_at',r['points'][0]);c.setFont('Helvetica-Bold',8);c.setFillColorRGB(.05,.27,.45)
                c.drawString(*xy([x,y]),r['id'])
        for part in b['parts']:
            for i,lead in enumerate(part['leads'],1):
                poly(lead['under_points'],(.35,.35,.35),.3)
                c.setFillColorRGB(0,0,0);c.circle(*xy(lead['points'][-1]),.65*mm,fill=1,stroke=0)
                if labels:
                    c.setFont('Helvetica',7);p=lead['hole'];c.drawString(*xy([p[0]+2,p[1]+2]),f'{part["id"]}.{i}')
    for hole in all_holes(b):
        c.setStrokeColorRGB(0,0,0);c.setLineWidth(.18*mm)
        x,y=xy(hole['center']);r=hole['diameter']/2*mm
        c.circle(x,y,r);c.line(x-r-1*mm,y,x+r+1*mm,y);c.line(x,y-r-1*mm,x,y+r+1*mm)
    c.setFont('Helvetica-Bold',9);c.setFillColorRGB(0,0,0)
    c.drawString(ox*mm,(oy+3)*mm,'BOTTOM / datum '+('at right' if mirror else 'at left'))


def ruler(c,x,y,length=100):
    c.setStrokeColorRGB(0,0,0);c.setLineWidth(.2*mm);c.line(x*mm,y*mm,(x+length)*mm,y*mm)
    for v in range(0,length+1,10):c.line((x+v)*mm,(y-1)*mm,(x+v)*mm,(y+1)*mm)
    c.setFont('Helvetica',8);c.drawString(x*mm,(y+3)*mm,f'{length} mm - check with a ruler')


def templates(layout,out):
    # An A3 portrait sheet has room for a 220 x 390 carrier at exact scale.
    c=canvas.Canvas(str(out/'drilling-templates-A3.pdf'),pagesize=(297*mm,420*mm))
    for b in layout['boards']:
        c.setFont('Helvetica-Bold',11);c.drawString(12*mm,411*mm,f'{b["id"]} / Rev {layout["revision"]} / COMPONENT FACE / 220 x 390 mm / 1:1')
        draw_board(c,b,38,12)
        c.saveState();c.translate(17*mm,85*mm);c.rotate(90);ruler(c,0,0);c.restoreState()
        c.setFont('Helvetica',8);c.drawString(12*mm,5*mm,'Print 100%. No Fit/Shrink. D3.5 lead/lacing/ties; D5 coil restraints and mounts.');c.showPage()
    c.save()
    c=canvas.Canvas(str(out/'drilling-templates-A4-tiled.pdf'),pagesize=(210*mm,297*mm))
    # Two columns and two rows, with shared registration marks in each overlap.
    origins=[(0,0),(40,0),(0,140),(40,140)]
    for b in layout['boards']:
        for n,(tx,ty) in enumerate(origins,1):
            c.setFont('Helvetica-Bold',10);c.drawString(10*mm,285*mm,f'{b["id"]} / Rev {layout["revision"]} / tile {n} of 4 / ACTUAL SIZE')
            c.setFont('Helvetica',8);c.drawString(10*mm,278*mm,f'Component face. Tile origin ({tx}, {ty}) mm. Match crosshairs; do not butt page edges.')
            c.saveState();path=c.beginPath();path.rect(10*mm,20*mm,180*mm,250*mm);c.clipPath(path,stroke=0)
            draw_board(c,b,10-tx,20-ty)
            for x,y in [(60,160),(160,160),(60,230),(160,230)]:
                px,py=(10+x-tx)*mm,(20+y-ty)*mm
                c.setStrokeColorRGB(.25,.25,.25);c.setLineWidth(.2*mm);c.rect(px-3*mm,py-3*mm,6*mm,6*mm)
                c.line(px-5*mm,py,px+5*mm,py);c.line(px,py-5*mm,px,py+5*mm)
            c.restoreState();ruler(c,15,10)
            c.saveState();c.translate(201*mm,70*mm);c.rotate(90);ruler(c,0,0);c.restoreState()
            c.setFont('Helvetica',7);c.drawString(120*mm,9*mm,'Square crosshairs: alignment only.')
            c.drawString(120*mm,5*mm,'D3.5 leads/ties; D5 mounts/coil ties.')
            c.showPage()
    c.save()


def wiring(layout,out):
    c=canvas.Canvas(str(out/'underside-wiring-A2.pdf'),pagesize=(594*mm,420*mm))
    for b in layout['boards']:
        c.setFont('Helvetica-Bold',14);c.drawString(12*mm,408*mm,f'{b["id"]} - UNDERSIDE WIRING / Rev {layout["revision"]}')
        draw_board(c,b,12,10,mirror=True,wiring=True)
        x,y=250,390
        def line(s,size=10):
            nonlocal y
            c.setFillColorRGB(0,0,0);c.setFont('Helvetica',size);c.drawString(x*mm,y*mm,s);y-=5.2
        line('MIRRORED: bottom edge remains at the bottom; component-face datum is at the right.',10)
        line('Blue: insulated 1.5 mm2 node wires. Grey: sleeved component tails. Black dot: joint.')
        line('Dashed outlines: components on the opposite face. Crossings without dots are insulated.')
        line('Hole centres remain component-face coordinates in the CSV. Drill from that face.')
        line('Turn wires through smooth 90-degree bends; the drawn vertices are routing guides.')
        line('Retain insulation between joints. Solder a 5 mm lead lap; sleeve the entire bare joint.')
        y-=4;line('COMPONENT ENDS: hole / destination wire / minimum routed tail length',11)
        for p in b['parts']:
            vals=[]
            for i,l in enumerate(p['leads'],1):vals.append(f'{i}: ({l["hole"][0]:g},{l["hole"][1]:g}) -> {l["rail"]}, {math.ceil(l["length_mm"]):g} mm')
            line(p['id']+'   '+' | '.join(vals),9)
        y-=4;line('NODE WIRES - cut lengths include fitting allowance',11)
        for r in b['rails']:line(f'{r["id"]} / {r["net"]}: {r["cut_length_mm"]:g} mm',9)
        y-=4;line('HARNESS ATTACHMENTS (component-face coordinates)',11)
        for name,(rid,pos) in b['terminals'].items():line(f'{name}: wire {rid}, ({pos[0]:g}, {pos[1]:g})',9)
        c.showPage()
    c.save()


def export(layout,out):
    out.mkdir(parents=True,exist_ok=True)
    result=audit(layout)
    with (out/'drilling-schedule.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['board','hole','kind','x_mm','y_mm','diameter_mm'])
        for b in layout['boards']:
            for h in all_holes(b):writer.writerow([b['id'],h['id'],h['kind'],*h['center'],h['diameter']])
    for b in layout['boards']:
        doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace();w,h,_=b['size_mm']
        for layer in ['OUTLINE','LEAD','RESTRAINT','WIRE_TIE','MOUNT','DIM']:doc.layers.new(layer)
        ms.add_lwpolyline([(0,0),(w,0),(w,h),(0,h)],close=True,dxfattribs={'layer':'OUTLINE'})
        for hole in all_holes(b):ms.add_circle(hole['center'],hole['diameter']/2,dxfattribs={'layer':{'lead':'LEAD','restraint':'RESTRAINT','wire_tie':'WIRE_TIE','mount':'MOUNT'}[hole['kind']]})
        for p1,p2,base,angle in [((0,0),(w,0),(0,-10),0),((0,0),(0,h),(-10,0),90)]:
            ms.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,override={'dimtxt':3,'dimasz':2.5,'dimlfac':1},dxfattribs={'layer':'DIM'}).render()
        target=out/f'{b["id"]}-drilling.dxf';doc.saveas(target)
        reopened=ezdxf.readfile(target)
        assert reopened.units==4 and len(reopened.modelspace().query('CIRCLE'))==len(all_holes(b))
        assert not reopened.audit().has_errors
    templates(layout,out);wiring(layout,out)
    (out/'template-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    print(json.dumps(export(json.loads(a.input.read_text()),a.out)))
