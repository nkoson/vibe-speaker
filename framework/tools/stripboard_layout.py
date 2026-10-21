#!/usr/bin/env python3
"""Compile and draw an existing-strip crossover layout; report geometry and routing.

Parts, pad assignments and routed native leads are input data. This tool neither
places components nor selects a layout. All coordinates are mm: u right, v rear,
z above the component face (copper is at negative substrate thickness).
"""
import argparse
import copy
import csv
import json
import math
from pathlib import Path
import numpy as np


def pad_xy(layout, pad):
    r, c = pad
    g = layout['grid']
    return [g['origin_mm'][0] + (c-1)*g['pitch_mm'],
            g['origin_mm'][1] + (r-1)*g['pitch_mm']]


def address(pad):
    return f'R{pad[0]:02d}C{pad[1]:02d}'


def route_length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def body_distance(points, body):
    """Signed distance to a box or finite circular cylinder."""
    p = np.asarray(points) - body['center_mm']
    if body['kind'] == 'box':
        q = np.abs(p) - np.asarray(body['size_mm'])/2
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(np.max(q, axis=1), 0)
    axis = 'XYZ'.index(body['axis'])
    radial = [i for i in range(3) if i != axis]
    q = np.column_stack((np.linalg.norm(p[:, radial], axis=1)-body['radius_mm'],
                         np.abs(p[:, axis])-body['length_mm']/2))
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(np.max(q, axis=1), 0)


def sampled_route(points, step=.25):
    result = []
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(math.dist(a,b)/step))
        result.extend(np.linspace(a,b,n+1))
    return np.asarray(result)


def inspect(layout):
    if len(set(layout['rows'].values())) != len(layout['rows']):
        raise ValueError('Distinct logical nodes must use distinct continuous strips')
    reports = dict(lead_routes=[], lead_body_clearances=[], body_box_gaps=[], hole_strip_clearances=[], hole_ligaments=[], lead_pair_clearances=[])
    parts = layout['parts']; leads=[]
    for p in parts:
        for i, lead in enumerate(p['leads']):
            points = lead['points_mm']; dest = pad_xy(layout,lead['pad'])
            if math.dist(points[-1], dest+[-layout['size_mm'][2]]) > 1e-6:
                raise ValueError(f"{p['id']}.{i+1}: route must end on its copper pad")
            if layout['rows'][p['nodes'][i]] != lead['pad'][0]:
                raise ValueError(f"{p['id']}.{i+1}: pad row disagrees with logical node")
            length=route_length(points)+lead.get('solder_tail_mm',2)
            reports['lead_routes'].append(dict(id=f"{p['id']}.{i+1}",net=p['nodes'][i],pad=address(lead['pad']),route_mm=length,required_free_mm=math.ceil(length),bends=max(0,len(points)-2)))
            samples=sampled_route(points);leads.append((f"{p['id']}.{i+1}",p['nodes'][i],samples,lead.get('sleeve_od_mm',1.5)))
            for other in parts:
                if other['id']==p['id']:continue
                gap=float(np.min(body_distance(samples,other['body'])))-lead.get('sleeve_od_mm',1.5)/2
                reports['lead_body_clearances'].append(dict(lead=f"{p['id']}.{i+1}",body=other['id'],gap_mm=gap))
    for i,(a,net,pts,od) in enumerate(leads):
        for b,net2,pts2,od2 in leads[i+1:]:
            # Discretization overestimates separation by at most the route sample step.
            gap=float(np.min(np.linalg.norm(pts[:,None,:]-pts2[None,:,:],axis=2)))-(od+od2)/2
            reports['lead_pair_clearances'].append(dict(leads=[a,b],same_net=net==net2,sampled_gap_mm=gap))
    for i,p in enumerate(parts):
        x,y=p['center_mm'];w,h,_=p['reserve_mm']
        for q in parts[i+1:]:
            xx,yy=q['center_mm'];ww,hh,_=q['reserve_mm'];dx=abs(x-xx)-(w+ww)/2;dy=abs(y-yy)-(h+hh)/2
            gap=math.hypot(max(dx,0),max(dy,0)) if max(dx,dy)>=0 else max(dx,dy)
            reports['body_box_gaps'].append(dict(parts=[p['id'],q['id']],reserve_gap_mm=gap))
    for h in layout['holes']:
        x,y=h['center_mm'];radius=h['diameter_mm']/2
        clear_radius=max(radius,h.get('copper_clearance_mm',0)/2)
        for net,row in layout['rows'].items():
            v=pad_xy(layout,[row,1])[1]
            reports['hole_strip_clearances'].append(dict(hole=h['id'],net=net,gap_mm=abs(y-v)-clear_radius-layout.get('strip_envelope_mm',2.54)/2))
        nearest=min((math.dist(h['center_mm'],q['center_mm'])-radius-q['diameter_mm']/2 for q in layout['holes'] if q['id']!=h['id']),default=math.inf)
        reports['hole_ligaments'].append(dict(hole=h['id'],edge_mm=min(x,y,layout['size_mm'][0]-x,layout['size_mm'][1]-y)-radius,nearest_hole_mm=nearest))
    reports['totals']=dict(native_lead_route_mm=sum(p['route_mm'] for p in reports['lead_routes']),native_lead_allowance_mm=sum(p['required_free_mm'] for p in reports['lead_routes']),native_lead_bends=sum(p['bends'] for p in reports['lead_routes']),added_extension_count=0,added_extension_cut_mm=0,assigned_rows=len(layout['rows']),parts=len(parts))
    return reports


def export_bodies(layout, folder):
    """Exact body-solid distances complement conservative footprint boxes."""
    import cadquery as cq
    assembly=cq.Assembly();shapes={};report=[]
    for p in layout['parts']:
        b=p['body'];center=cq.Vector(*b['center_mm'])
        if b['kind']=='box':
            w,h,t=b['size_mm'];shape=cq.Solid.makeBox(w,h,t,center-cq.Vector(w/2,h/2,t/2))
        else:
            direction=cq.Vector(*{'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[b['axis']])
            shape=cq.Solid.makeCylinder(b['radius_mm'],b['length_mm'],center-direction*b['length_mm']/2,direction)
        shapes[p['id']]=shape;assembly.add(shape,name=p['id'])
    for i,(name,shape) in enumerate(shapes.items()):
        for other,second in list(shapes.items())[i+1:]:
            report.append(dict(parts=[name,other],distance_mm=shape.distance(second),overlap_mm3=shape.intersect(second).Volume()))
    assembly.export(str(folder/'component-bodies.step'))
    return report


def compile_circuit(layout,circuit,copper_multiplier=1):
    out=copy.deepcopy(circuit);out['wires']=[];taps={};parts={p['id']:p for p in layout['parts']};entries=[]
    if set(parts)!={c['id'] for c in out['components']}:raise ValueError('Physical and electrical part IDs differ')
    def wire(id,a,b,r):out['wires'].append(dict(id=id,**{'from':a,'to':b},resistance_ohm=r))
    for c in out['components']:
        p=parts[c['id']]
        for i,l in enumerate(p['leads']):
            rc=l['pad'];tag=address(rc);taps[tag]=rc
            mm=route_length(l['points_mm'])+l.get('solder_tail_mm',2)
            resistance=layout.get('rho_ohm_mm2_m',.0175)*mm/1000/l.get('section_mm2',.5)+layout.get('joint_ohm',.001)
            wire(f"lead_{p['id']}_{i+1}",c['nodes'][i],tag,resistance)
            entries.append(dict(id=f"{p['id']}.{i+1}",pad=tag,length_mm=mm,resistance_ohm=resistance))
    for h in layout['harness']:
        tag=address(h['pad']);taps[tag]=h['pad']
        resistance=(layout.get('rho_ohm_mm2_m',.0175)*h['length_mm']/1000/h.get('section_mm2',1.5)+2*layout.get('joint_ohm',.001)
                    if 'length_mm' in h else h['resistance_ohm'])
        wire(h['id'],h['node'],tag,resistance)
    for row in layout['rows'].values():
        pp=sorted((rc[1],name) for name,rc in taps.items() if rc[0]==row)
        for (a,pa),(b,pb) in zip(pp,pp[1:]):
            wire(f'copper_R{row}_{a}_{b}',pa,pb,(b-a)*layout['grid']['pitch_mm']*layout['copper_ohm_per_mm']*copper_multiplier)
    return out,entries


def draw(layout,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Circle
    colors=['#b64438','#a96d16','#286c90','#7b4fa0','#288562','#a94078','#23549b']
    palette=dict(zip(layout['rows'],colors));w,h,_=layout['size_mm']
    for copper in [False,True]:
        fig,ax=plt.subplots(figsize=(12,8));ax.set_aspect('equal');ax.set_xlim(-5,w+24);ax.set_ylim(h+5,-8)
        flip=lambda x:w-x if copper else x
        ax.add_patch(Rectangle((0,0),w,h,fc='#faf8ed',ec='#333',lw=1.5))
        for net,row in layout['rows'].items():
            y=pad_xy(layout,[row,1])[1];ax.plot([1,w-1],[y,y],color=palette[net],ls='-' if copper else '--',alpha=1 if copper else .4,lw=2 if copper else 1)
            ax.text(w+2,y,f'R{row:02} {net}',va='center',fontsize=9,color=palette[net])
        if not copper:
            for p in layout['parts']:
                x,y=p['center_mm'];bw,bh=p['footprint_mm'];fc={'L':'#dcb38d','C':'#b2d1bf','R':'#e7c88e'}[p['id'][0]]
                shape=Circle((x,y),bw/2,fc=fc,ec='#444') if p['body'].get('axis')=='Z' else Rectangle((x-bw/2,y-bh/2),bw,bh,fc=fc,ec='#444')
                ax.add_patch(shape);ax.text(x,y,p['id'],ha='center',va='center',fontsize=11,fontweight='bold',zorder=20,bbox=dict(facecolor=fc,edgecolor='none',alpha=.9,pad=.8))
                if p['id'][0]=='L':ax.text(x,y+4,'axis '+p['body']['axis'],fontsize=7,ha='center')
                for i,lead in enumerate(p['leads']):
                    pts=np.asarray(lead['points_mm']);ax.plot(pts[:,0],pts[:,1],color=palette[p['nodes'][i]],lw=1.5,ls='--' if lead.get('under_body') else '-')
                    a,b=pts[0],pts[-1];ax.text(a[0]+.5,a[1]-.8,str(i+1),fontsize=7);ax.plot(b[0],b[1],'o',mfc='white',mec=palette[p['nodes'][i]],ms=4)
        for hole in layout['holes']:
            x,y=hole['center_mm'];x=flip(x);color='#222' if hole['role']=='mount' else '#9a6336' if hole['role']=='tie' else '#398063'
            if copper and hole.get('copper_clearance_mm'):ax.add_patch(Circle((x,y),hole['copper_clearance_mm']/2,fc='white',ec=color,ls='--',lw=.6))
            ax.add_patch(Circle((x,y),hole['diameter_mm']/2,fc='white',ec=color,lw=.8))
        if copper:
            for p in layout['parts']:
                for i,lead in enumerate(p['leads']):
                    x,y=pad_xy(layout,lead['pad']);ax.plot(flip(x),y,'o',ms=4,mfc='white',mec=palette[p['nodes'][i]])
                    ax.text(flip(x),y-1.5,f"{p['id']}.{i+1}",fontsize=7,ha='center',rotation=30)
        for cable in layout['harness']:
            x,y=pad_xy(layout,cable['pad']);ax.plot(flip(x),y,'s',ms=5,mfc='#ffe099',mec='#333')
            if copper and cable.get('points_mm'):
                pts=np.asarray(cable['points_mm']);ax.plot([flip(x) for x in pts[:,0]],pts[:,1],color=palette[cable['net']],lw=1.5,ls='--')
            if copper:ax.text(flip(x),y+3,cable['label'],fontsize=6,ha='center',rotation=30)
        ax.text(w/2,-5,'FRONT / baffle',ha='center',fontsize=11)
        ax.set_title(layout['title']+' - '+('copper face' if copper else 'component face and native leads'),fontsize=14,pad=15)
        ax.set_xlabel('Mirrored u (mm)' if copper else 'u (mm)');ax.set_ylabel('v (mm)');ax.set_xticks(range(0,int(w)+1,10));ax.set_yticks(range(0,int(h)+1,10));ax.grid(alpha=.10)
        name='copper-face' if copper else 'component-face'
        fig.savefig(folder/(name+'.png'),dpi=200,bbox_inches='tight');fig.savefig(folder/(name+'.svg'),bbox_inches='tight');plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--circuit',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--draw',action='store_true');p.add_argument('--cad',action='store_true');args=p.parse_args()
    layout=json.loads(args.input.read_text());circuit=json.loads(args.circuit.read_text());report=inspect(layout);args.out.mkdir(parents=True,exist_ok=True)
    for mult in [1,2]:
        net,rows=compile_circuit(layout,circuit,mult);(args.out/f'board_{mult}x.params.json').write_text(json.dumps(net,indent=2)+'\n')
    if args.cad:report['exact_body_pairs']=export_bodies(layout,args.out)
    (args.out/'layout-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    with (args.out/'lead-schedule.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=report['lead_routes'][0].keys());writer.writeheader();writer.writerows(report['lead_routes'])
    if args.draw:draw(layout,args.out)
    print(json.dumps(report['totals']))
if __name__=='__main__':main()
