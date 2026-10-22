#!/usr/bin/env python3
"""Build fabrication PDF/DXF sheets and STEP parts from a millimetre CAD manifest.

  .speaker-venv/bin/python framework/tools/cad_drawings.py --input drawing.json --out final/cad --pdf final/cabinet-sheets.pdf

Project-specific geometry and sheet layout are data. This tool performs geometry,
annotation, export and geometric checks; it does not choose an acoustic design.
"""
import argparse, json, math, hashlib, re
import copy
from pathlib import Path
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

PAPERS={'A1':(841,594),'A2':(594,420),'A3':(420,297)}
WEIGHTS={'OUTLINE':.5,'HIDDEN':.25,'CENTER':.25,'CUT':.5,'DIM':.25,'HATCH':.13,'ENVELOPE':.25,'LINING':.13}
DASHES={'HIDDEN':[2,1],'CENTER':[6,1,1,1],'CUT':[8,2,1,2],'ENVELOPE':[6,1,1,1,1,1]}

def dimension_text(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')

def hatch_boundary_flags(loops):
    """External islands are flagged independently of interior void loops."""
    def contains(point,loop):
        x,y=point;inside=False
        for a,b in zip(loop,loop[1:]+loop[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
                inside=not inside
        return inside
    return [1 if sum(contains(loop[0],other) for j,other in enumerate(loops) if j!=i)%2==0 else 0
            for i,loop in enumerate(loops)]

def flared_duct_entities(spec):
    """Longitudinal section of purchased flare/tube pieces and joint sleeves."""
    bore=spec['bore_mm']/2;mouth=spec['mouth_mm']/2;r=mouth-bore
    outer,centre,inner=spec['piece_lengths_mm'];wall=spec['wall_mm']
    gap=spec.get('explode_gap_mm',0);sleeve=spec['sleeve_mm']
    if min(outer,inner)<r or centre<=0 or wall<=0 or r<=0:
        raise ValueError('flared duct lengths must contain their end profiles')
    starts=[0,outer+gap,outer+centre+2*gap];entities=[]
    curve=[(r-r*math.cos(a),mouth-r*math.sin(a)) for a in [i*math.pi/96 for i in range(49)]]
    for index,(start,length) in enumerate(zip(starts,[outer,centre,inner])):
        inside=curve+[(length,bore)] if index==0 else [(0,bore),(length,bore)] if index==1 else [(0,bore)]+[(length-x,y) for x,y in reversed(curve)]
        outside=[(x,y+wall) for x,y in inside]
        for sign in [-1,1]:
            loop=[[start+x,sign*y] for x,y in inside]+[[start+x,sign*y] for x,y in reversed(outside)]
            entities.append(dict(kind='hatch',loops=[loop],angle=45 if index!=1 else -45))
    flange=spec['flange_mm']/2;thickness=spec['flange_thickness_mm']
    for sign in [-1,1]:
        entities.append(dict(kind='rect',xy=[0,mouth if sign>0 else -flange],size=[thickness,flange-mouth]))
    if not gap:
        for joint in [outer,outer+centre]:
            for sign in [-1,1]:
                y=bore+wall if sign>0 else -bore-wall-spec['sleeve_wall_mm']
                entities.append(dict(kind='rect',xy=[joint-sleeve/2,y],size=[sleeve,spec['sleeve_wall_mm']]))
    entities.append(dict(kind='line',points=[[-12,0],[starts[-1]+inner+12,0]],layer='CENTER'))
    return entities


def rounded_points(x,y,w,h,r):
    if not r:return [(x,y,0),(x+w,y,0),(x+w,y+h,0),(x,y+h,0)]
    b=math.tan(math.pi/8)
    return [(x+r,y,0),(x+w-r,y,b),(x+w,y+r,0),(x+w,y+h-r,b),
            (x+w-r,y+h,0),(x+r,y+h,b),(x,y+h-r,0),(x,y+r,b)]


def part_entities(part,face='outside',features=None,outline=True):
    entities=[]
    if outline:
        if part.get('profile_entities'):entities.extend(part['profile_entities'])
        elif part.get('outline')=='circle':entities.append(dict(kind='circle',center=part['center'],radius=part['diameter']/2,layer='OUTLINE',id='outline'))
        else:entities.append(dict(kind='rect',xy=[0,0],size=[part['width'],part['height']],layer='OUTLINE',id='outline'))
    for feature in part.get('features',[]):
        if feature.get('in_profile'):continue
        if features is not None and feature['id'] not in features:continue
        e=dict(feature);e['layer']='OUTLINE' if feature.get('face','outside')==face or feature.get('depth')=='through' else 'HIDDEN'
        if e['kind']=='edge_hole':
            x,y,z=e['position'];dx,dy,dz=e['direction'];r=e['diameter']/2;depth=e['depth']
            if abs(dy)>.9:e=dict(kind='rect',xy=[x-r,min(y,y+dy*depth)],size=[2*r,depth],layer='HIDDEN',id=e['id'])
            else:e=dict(kind='line',points=[[x,y],[x+dx*depth,y+dy*depth]],layer='HIDDEN',id=e['id'])
        elif e['kind'] in ('circle','countersink'):
            e['kind']='circle';e['radius']=e.pop('diameter')/2
        entities.append(e)
        if feature.get('edge_radius'):
            r=feature['edge_radius']
            if feature['kind']=='circle':
                entities.append(dict(kind='circle',center=feature['center'],
                                     radius=feature['diameter']/2+r,layer='OUTLINE'))
            elif feature['kind']=='rect':
                x,y=feature['xy'];w,h=feature['size']
                entities.append(dict(kind='rect',xy=[x-r,y-r],size=[w+2*r,h+2*r],
                                     radius=feature.get('radius',0)+r,layer='OUTLINE'))
    return entities


def make_part(part):
    import cadquery as cq
    if 'solid_model' in part:
        from cad_components import make_component
        return make_component(part['solid_model'])
    t=float(part['thickness'])
    if t<=0:raise ValueError('part thickness must be positive')
    if part.get('outline')=='circle':
        shape=cq.Workplane('XY').center(*part['center']).circle(part['diameter']/2).extrude(-t).val()
    elif part.get('miter'):
        w,h=part['width'],part['height']
        if min(w,h)<=2*t:raise ValueError('miter leaves no inner face')
        outside=cq.Workplane('XY').center(w/2,h/2).rect(w,h).val()
        inside=cq.Workplane('XY',origin=(0,0,-t)).center(w/2,h/2).rect(w-2*t,h-2*t).val()
        shape=cq.Solid.makeLoft([outside,inside],ruled=True)
    else:shape=cq.Workplane('XY').box(part['width'],part['height'],t,centered=False).translate((0,0,-t)).val()
    for feature in part.get('features',[]):
        kind=feature['kind'];depth=t if feature.get('depth')=='through' else float(feature['depth'])
        if depth<=0 or depth>t+1e-8 and kind!='edge_hole':raise ValueError('invalid machining depth: '+feature['id'])
        if kind=='edge_hole':
            cutter=cq.Solid.makeCylinder(feature['diameter']/2,depth,cq.Vector(*feature['position']),cq.Vector(*feature['direction']))
        else:
            z=-t if feature.get('face','outside')=='inside' else -depth
            if kind=='circle':cutter=cq.Solid.makeCylinder(feature['diameter']/2,depth,cq.Vector(*feature['center'],z))
            elif kind=='countersink':
                x,y=feature['center'];large=feature['diameter']/2;small=feature['bore']/2
                if feature.get('face','outside')=='inside':
                    cutter=cq.Solid.makeCone(large,small,depth,cq.Vector(x,y,-t))
                else:cutter=cq.Solid.makeCone(small,large,depth,cq.Vector(x,y,-depth))
            elif kind=='rect':
                x,y=feature['xy'];w,h=feature['size'];cutter=cq.Workplane('XY').box(w,h,depth,centered=False)
                if feature.get('radius'):cutter=cutter.edges('|Z').fillet(feature['radius'])
                cutter=cutter.translate((x,y,z)).val()
            else:raise ValueError('unknown feature '+kind)
        shape=shape.cut(cutter)
    for feature in part.get('features',[]):
        if not feature.get('edge_radius'):continue
        if feature['depth']!='through':
            raise ValueError('edge roundover requires a through aperture')
        if feature['kind']=='circle':
            x,y=feature['center'];radius=feature['diameter']/2
            edges=[e for e in shape.Edges() if e.geomType()=='CIRCLE'
                   and abs(e.radius()-radius)<1e-6
                   and abs(e.arcCenter().x-x)<1e-6 and abs(e.arcCenter().y-y)<1e-6
                   and min(abs(e.arcCenter().z),abs(e.arcCenter().z+t))<1e-6]
            if len(edges)!=2:raise ValueError('roundover requires two complete aperture rims')
        elif feature['kind']=='rect':
            x,y=feature['xy'];w,h=feature['size'];edges=[]
            for e in shape.Edges():
                b=e.BoundingBox()
                if b.zlen<1e-5 and min(abs(b.zmin),abs(b.zmin+t))<1e-5 and b.xmin>=x-1e-5 and b.xmax<=x+w+1e-5 and b.ymin>=y-1e-5 and b.ymax<=y+h+1e-5:
                    edges.append(e)
            if len(edges)<8:raise ValueError('roundover requires two complete rectangular rims')
        else:raise ValueError('unsupported rounded aperture kind')
        shape=shape.fillet(feature['edge_radius'],edges)
    if not shape.isValid() or shape.Volume()<=0:raise ValueError('invalid solid '+part['id'])
    return shape


def place_part(shape,placement):
    import cadquery as cq
    plane=cq.Plane(origin=placement['origin'],xDir=placement.get('x_dir',[1,0,0]),normal=placement.get('normal',[0,0,1]))
    return shape.located(plane.location)

def aperture_metrics(part):
    """Root-contour area and material ligaments; interpretation stays external."""
    import cadquery as cq
    features=[f for f in part.get('features',[]) if f.get('role')=='air_aperture']
    if not features:return None
    wires=[];areas=[]
    for f in features:
        if f['kind']=='circle':
            face=cq.Face.makeFromWires(cq.Workplane('XY').center(*f['center']).circle(f['diameter']/2).val())
        elif f['kind']=='rect':
            x,y=f['xy'];w,h=f['size']
            block=cq.Workplane('XY').box(w,h,1,centered=False)
            if f.get('radius'):block=block.edges('|Z').fillet(f['radius'])
            face=block.faces('<Z').val().translate((x,y,0))
        else:raise ValueError('unsupported air aperture')
        wires.append(face.outerWire());areas.append(face.Area())
    boundary=copy.deepcopy(part)
    boundary['features']=[f for f in boundary.get('features',[]) if f.get('role')!='air_aperture']
    section=cq.Workplane('XY',origin=(0,0,-part['thickness']/2)).add(make_part(boundary)).section()
    contours=section.wires().vals()
    outline=max(contours,key=lambda w:w.Length()).translate((0,0,part['thickness']/2))
    pairs=[dict(a=features[i]['id'],b=features[j]['id'],distance_mm=a.distance(b))
           for i,a in enumerate(wires) for j,b in enumerate(wires) if i<j]
    rims=[dict(id=f['id'],distance_mm=w.distance(outline)) for f,w in zip(features,wires)]
    return dict(apertures=len(features),areas_mm2=areas,total_area_mm2=sum(areas),
                pair_ligaments=pairs,rim_ligaments=rims)


def export_solids(spec,out):
    import cadquery as cq
    folder=out/'step';folder.mkdir(exist_ok=True)
    shapes={};report=[];assembly=cq.Assembly(name=spec['meta']['drawing_prefix'])
    domain=spec.get('air_domain')
    air=cq.Workplane('XY').box(*domain['size_mm'],centered=False).translate(tuple(domain['origin_mm'])).val() if domain else None
    for part in spec.get('parts',[]):
        shape=make_part(part);shapes[part['id']]=shape
        cq.exporters.export(shape,str(folder/(part['id']+'.step')))
        reopened=cq.importers.importStep(str(folder/(part['id']+'.step'))).val()
        # Adaptive integration is necessary for trimmed B-spline lofts. Default
        # mass integration can change appreciably after STEP seam normalization.
        integration_tol=1e-5 if 'solid_model' in part else None
        original_volume=shape.Volume(integration_tol);exported_volume=reopened.Volume(integration_tol)
        relative_tolerance=1e-6 if integration_tol else 1e-8
        if abs(exported_volume-original_volume)>max(1e-5,original_volume*relative_tolerance):raise ValueError('STEP volume mismatch: '+part['id'])
        if not reopened.isValid() or len(reopened.Solids())!=len(shape.Solids()):raise ValueError('STEP topology mismatch')
        # Draw and assemble the reopened exchange solid, including normalized
        # seams/tolerances on complex revolved and boolean purchased parts.
        shape=reopened;shapes[part['id']]=shape
        bb=shape.BoundingBox();entry=dict(id=part['id'],volume_mm3=exported_volume,bounds_mm=[bb.xlen,bb.ylen,bb.zlen],features=len(part.get('features',[])),solid_count=len(shape.Solids()),step_volume_difference_mm3=exported_volume-original_volume,volume_integration_tolerance=integration_tol)
        report.append(entry)
        metrics=aperture_metrics(part)
        if metrics:entry['aperture_geometry']=metrics
        if air is not None:entry['air_intrusions_mm3']=[]
        for j,pose in enumerate(part.get('placements',[])):
            placed=place_part(shape,pose);shapes[f"{part['id']}@{j}"]=placed
            assembly.add(placed,name=part['id']+'_'+str(j),color=cq.Color(*part.get('color',[.77,.68,.52])))
            if air is not None:entry['air_intrusions_mm3'].append(placed.intersect(air).Volume())
    assembly.export(str(folder/'cabinet-assembly.step'))
    return shapes,report


def section_entities(shapes,spec):
    import cadquery as cq
    plane=cq.Plane(origin=spec['origin'],xDir=spec['x_dir'],normal=spec['normal']);entities=[]
    for i,name in enumerate(spec['parts']):
        sec=cq.Workplane(plane).add(shapes[name]).section()
        loops=[]
        for wire in sec.wires().vals():
            points,_=wire.sample(.05)
            local=[plane.toLocalCoords(p) for p in points]
            if len(local)>2:loops.append([[p.x,p.y] for p in local])
        if loops:entities.append(dict(kind='hatch',loops=loops,layer='HATCH',angle=45 if i%2==0 else -45))
    return entities


class Sheet:
    def __init__(self,c,spec,meta,index,total,out):
        self.c=c;self.spec=spec;self.meta=meta;self.out=out;self.index=index;self.total=total
        self.W,self.H=PAPERS[spec.get('paper','A3')];c.setPageSize((self.W*mm,self.H*mm))
        self.stroke('DIM');c.rect(10*mm,10*mm,(self.W-20)*mm,(self.H-20)*mm)
        # Ruled title block in paper coordinates; draw no artwork behind it.
        c.line(10*mm,42*mm,(self.W-10)*mm,42*mm)
        tx=max(10,self.W-230);c.line(tx*mm,10*mm,tx*mm,42*mm)
        for y in [20,31]:c.line(tx*mm,y*mm,(self.W-10)*mm,y*mm)
        self.text(tx+3,35,meta['title']+' / '+spec['title'],3.3,bold=True,max_width=self.W-tx-7)
        self.text(tx+3,24,f"{meta['drawing_prefix']}-{spec['id']}  |  REV {meta['revision']}  |  {meta['date']}",2.5)
        self.text(tx+3,14,f"{spec.get('paper','A3')}  |  mm  |  {meta.get('projection','THIRD ANGLE')}  |  {index}/{total}",2.5)
        self.text(14,35,'MATERIAL: PER PART / '+meta.get('change','FABRICATION DRAWING').upper(),2.5,bold=True,max_width=tx-19)
        self.text(14,29,'Model geometry 1:1; plot each view at its marked scale.',2.5)
        self.text(14,23,meta.get('tolerance_note','Use the stated datums and dimensions.'),2.5,max_width=tx-19)
        self.text(14,17,'Solid: visible / dash: hidden / chain: axis / hatch: section',2.5,max_width=tx-19)
        self.text(14,self.H-7,spec['id']+'  '+spec['title'].upper(),3.0,bold=True)
        self.views=[]
    def stroke(self,layer):
        self.c.setStrokeColorRGB(0,0,0);self.c.setLineWidth(WEIGHTS.get(layer,.25)*mm);self.c.setDash([x*mm for x in DASHES.get(layer,[])])
    def text(self,x,y,text,height=2.5,bold=False,max_width=None):
        size=height*mm;self.c.setFillColorRGB(0,0,0);font='Helvetica-Bold' if bold else 'Helvetica'
        # Wrap notes instead of silently shrinking text.
        lines=[]
        for raw in str(text).split('\n'):
            line=''
            for word in raw.split():
                trial=(line+' '+word).strip()
                if max_width and line and stringWidth(trial,font,size)>max_width*mm:lines.append(line);line=word
                else:line=trial
            lines.append(line)
        self.c.setFont(font,size)
        for i,line in enumerate(lines):self.c.drawString(x*mm,(y-i*height*1.45)*mm,line)
    def table(self,record):
        x,y=record['at'];widths=record['widths'];height=record.get('row_height',7)
        for row_index,row in enumerate([record['headers']]+record['rows']):
            xx=x;yy=y-row_index*height;self.stroke('DIM');self.c.line(x*mm,yy*mm,(x+sum(widths))*mm,yy*mm)
            for value,w in zip(row,widths):self.text(xx+1,yy-4.5,value,record.get('text_height',2.5),bold=row_index==0,max_width=w-2);xx+=w
    def finish(self):self.c.showPage()


class View:
    def __init__(self,sheet,spec):
        self.sheet=sheet;self.c=sheet.c;self.spec=spec;self.scale=float(spec['scale']);self.at=spec['at'];self.offset=spec.get('origin',[0,0]);self.audit=[]
        if self.scale<=0:raise ValueError('scale must be positive')
        self.doc=ezdxf.new('R2010',setup=True);self.doc.units=4;self.doc.header['$MEASUREMENT']=1;self.doc.header['$LTSCALE']=1/self.scale;self.m=self.doc.modelspace()
        for layer,lw in WEIGHTS.items():self.doc.layers.new(layer,dxfattribs={'color':7,'lineweight':round(lw*100),'linetype':'DASHED' if layer=='HIDDEN' else 'CENTER' if layer in ['CENTER','CUT','ENVELOPE'] else 'CONTINUOUS'})
        self.style={'dimtxt':2.8/self.scale,'dimasz':2/self.scale,'dimexo':1/self.scale,'dimexe':1.5/self.scale,'dimgap':1/self.scale,'dimtad':1,'dimdec':2,'dimzin':8,
                    'dimlfac':1,'dimscale':1,'dimtsz':0,'dimblk':'','dimtxsty':'Standard','dimlunit':2,'dimdsep':46}
        label=spec.get('label',spec['id'])
        ratio=f'{self.scale:g}:1' if self.scale>=1 else f'1:{1/self.scale:g}'
        self.sheet.text(*spec.get('label_at',[self.at[0],self.at[1]-14]),f"{label}   SCALE {ratio}",3,bold=True)
        self.byid={}
    def xy(self,p):return ((self.at[0]+(p[0]-self.offset[0])*self.scale)*mm,(self.at[1]+(p[1]-self.offset[1])*self.scale)*mm)
    def line(self,a,b,layer='OUTLINE',native=True):
        self.sheet.stroke(layer);self.c.line(*self.xy(a),*self.xy(b))
        if native:self.m.add_line(a,b,dxfattribs={'layer':layer})
    def text(self,p,text,height=2.5,rotation=0,native=True):
        x,y=self.xy(p);self.c.saveState();self.c.translate(x,y);self.c.rotate(rotation);self.c.setFillColorRGB(0,0,0);self.c.setFont('Helvetica',height*mm);self.c.drawString(0,0,str(text));self.c.restoreState()
        if native:self.m.add_text(str(text),dxfattribs={'height':height/self.scale,'insert':p,'rotation':rotation,'layer':'DIM'})
    def entity(self,e):
        kind=e['kind'];layer=e.get('layer','OUTLINE');self.sheet.stroke(layer)
        if 'id' in e:self.byid[e['id']]=e
        if kind=='line':self.line(*e['points'],layer)
        elif kind=='polyline':
            pts=e['points'];p=self.c.beginPath();p.moveTo(*self.xy(pts[0]));
            for q in pts[1:]:p.lineTo(*self.xy(q))
            if e.get('closed',True):p.close()
            self.c.drawPath(p);self.m.add_lwpolyline(pts,close=e.get('closed',True),dxfattribs={'layer':layer})
        elif kind=='rect':
            x,y=e['xy'];w,h=e['size'];r=e.get('radius',0);xx,yy=self.xy((x,y));self.c.roundRect(xx,yy,w*self.scale*mm,h*self.scale*mm,r*self.scale*mm,stroke=1,fill=0)
            self.m.add_lwpolyline(rounded_points(x,y,w,h,r),format='xyb',close=True,dxfattribs={'layer':layer})
        elif kind=='circle':
            self.c.circle(*self.xy(e['center']),e['radius']*self.scale*mm,stroke=1,fill=0);self.m.add_circle(e['center'],e['radius'],dxfattribs={'layer':layer})
        elif kind=='arc':
            x,y=self.xy(e['center']);r=e['radius']*self.scale*mm
            self.c.arc(x-r,y-r,x+r,y+r,e['start'],(e['end']-e['start'])%360)
            self.m.add_arc(e['center'],e['radius'],e['start'],e['end'],dxfattribs={'layer':layer})
        elif kind=='hatch':
            loops=e['loops'];path=self.c.beginPath()
            for loop in loops:
                path.moveTo(*self.xy(loop[0]));
                for q in loop[1:]:path.lineTo(*self.xy(q))
                path.close()
            self.c.saveState();self.c.clipPath(path,stroke=0,fill=0,fillMode=0);self.sheet.stroke('HATCH')
            pts=[self.xy(q) for loop in loops for q in loop];xs=[q[0] for q in pts];ys=[q[1] for q in pts];x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys);span=y1-y0
            n=int((x1-x0+2*span)/(2*mm))+2
            for i in range(n):
                x=x0-span+i*2*mm;self.c.line(x,y0,x+(span if e.get('angle',45)>0 else -span),y1)
            self.c.restoreState()
            h=self.m.add_hatch(dxfattribs={'layer':'HATCH'});h.set_pattern_fill('ANSI31',scale=1/self.scale,angle=0 if e.get('angle',45)>0 else 90)
            h.dxf.hatch_style=0
            for loop,flags in zip(loops,hatch_boundary_flags(loops)):
                h.paths.add_polyline_path(loop,is_closed=True,flags=flags)
            for loop in loops:self.entity(dict(kind='polyline',points=loop,layer='OUTLINE'))
        else:raise ValueError('unsupported drawing entity '+kind)
    def arrow(self,tip,direction,native=False):
        x,y=self.xy(tip);a=math.atan2(direction[1],direction[0]);length=2*mm;width=.65*mm
        p=self.c.beginPath();p.moveTo(x,y);p.lineTo(x+length*math.cos(a)+width*math.sin(a),y+length*math.sin(a)-width*math.cos(a));p.lineTo(x+length*math.cos(a)-width*math.sin(a),y+length*math.sin(a)+width*math.cos(a));p.close();self.c.setFillColorRGB(0,0,0);self.c.drawPath(p,fill=1,stroke=0)
        if native:
            length=2/self.scale;width=.65/self.scale;x,y=tip
            self.m.add_solid([tip,(x+length*math.cos(a)+width*math.sin(a),y+length*math.sin(a)-width*math.cos(a)),(x+length*math.cos(a)-width*math.sin(a),y+length*math.sin(a)+width*math.cos(a))],dxfattribs={'layer':'DIM'})
    def dimension(self,d):
        p1,p2=d['p1'],d['p2'];angle=d.get('angle',0);base=d['base'];horizontal=angle==0;value=abs(p2[0]-p1[0]) if horizontal else abs(p2[1]-p1[1]);text=dimension_text(value)+(' REF' if d.get('reference') else '')
        dim=self.m.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,text='<>'+(' REF' if d.get('reference') else ''),override=self.style,dxfattribs={'layer':'DIM'});dim.render();self.audit.append({'kind':'linear','value_mm':value,'entity_handle':dim.dimension.dxf.handle})
        a=(p1[0],base[1]) if horizontal else (base[0],p1[1]);b=(p2[0],base[1]) if horizontal else (base[0],p2[1]);gap=1/self.scale;extra=1.5/self.scale
        for p,q in [(p1,a),(p2,b)]:
            direction=(1 if q[1]>=p[1] else -1) if horizontal else (1 if q[0]>=p[0] else -1)
            start=(p[0],p[1]+gap*direction) if horizontal else (p[0]+gap*direction,p[1]);end=(q[0],q[1]+extra*direction) if horizontal else (q[0]+extra*direction,q[1]);self.line(start,end,'DIM',native=False)
        self.line(a,b,'DIM',native=False);direction=(b[0]-a[0],b[1]-a[1]);self.arrow(a,direction);self.arrow(b,(-direction[0],-direction[1]))
        mid=((a[0]+b[0])/2,(a[1]+b[1])/2);self.text((mid[0]+(2/self.scale if not horizontal else -len(text)*.7/self.scale),mid[1]+(2/self.scale if horizontal else -len(text)*.7/self.scale)),text,2.8,0 if horizontal else 90,native=False)
    def leader(self,d,native=True):
        points=d['points'];
        for a,b in zip(points,points[1:]):self.line(a,b,'DIM',native=native)
        self.arrow(points[0],(points[1][0]-points[0][0],points[1][1]-points[0][1]),native=native);self.text(points[-1],d['text'],d.get('height',2.5),native=native)
    def diameter(self,d):
        e=self.byid[d['feature']];center=e['center'];radius=e['radius'];angle=math.radians(d.get('angle',30));tip=[center[0]+radius*math.cos(angle),center[1]+radius*math.sin(angle)];target=d['location'];prefix=d.get('prefix','');suffix=d.get('suffix','')
        dim=self.m.add_diameter_dim(center=center,radius=radius,angle=math.degrees(angle),location=target,override=self.style,dxfattribs={'layer':'DIM'})
        dim.dimension.dxf.text=f'{prefix}<>{suffix}';dim.render();self.audit.append({'kind':'diameter','value_mm':2*radius,'entity_handle':dim.dimension.dxf.handle})
        self.leader({'points':[tip,target],'text':f'{prefix}D{dimension_text(2*radius)}{suffix}'},native=False)
    def finish(self):
        folder=self.sheet.out/'dxf';folder.mkdir(exist_ok=True);name=self.sheet.spec['id']+'_'+self.spec['id'];p=folder/(name+'.dxf');self.doc.saveas(p)
        reopened=ezdxf.readfile(p);audit=reopened.audit();
        if audit.has_errors:raise ValueError('DXF structural audit failed: '+name)
        for dim in self.audit:
            entity=reopened.entitydb[dim['entity_handle']];measured=entity.get_measurement()
            if abs(float(measured)-dim['value_mm'])>1e-7:raise ValueError('dimension mismatch: '+name)
            labels=[e.plain_text() for e in reopened.blocks[entity.dxf.geometry].query('TEXT MTEXT')]
            number=dimension_text(dim['value_mm'])
            if not any(re.search(r'(?<![\d.])'+re.escape(number)+r'(?![\d.])',label) for label in labels):
                raise ValueError('rendered dimension label mismatch: '+name)
            dim['rendered_text']=labels
        return dict(view=name,scale=self.scale,units='mm',entities=len(self.m),dimensions=self.audit,file=str(p))


def build(spec,out,pdf_path):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);pdf_path=Path(pdf_path);pdf_path.parent.mkdir(parents=True,exist_ok=True)
    shapes,solids=export_solids(spec,out) if spec.get('parts') else ({},[])
    parts={p['id']:p for p in spec.get('parts',[])};c=canvas.Canvas(str(pdf_path));c.setTitle(spec['meta']['title']+' - cabinet CAD drawings');records=[]
    for i,record in enumerate(spec['sheets'],1):
        sheet=Sheet(c,record,spec['meta'],i,len(spec['sheets']),out)
        for v in record.get('views',[]):
            view=View(sheet,v)
            entities=part_entities(parts[v['part']],v.get('face','outside'),v.get('features'),v.get('outline',True)) if 'part' in v else []
            if 'section' in v:entities+=section_entities(shapes,v['section'])
            if 'projection' in v:
                from cad_components import projection_entities
                entities+=projection_entities(shapes,v['projection'])
            if 'flared_duct' in v:entities+=flared_duct_entities(v['flared_duct'])
            entities+=v.get('entities',[])
            for e in entities:view.entity(e)
            for d in v.get('dimensions',[]):view.dimension(d)
            for d in v.get('diameters',[]):view.diameter(d)
            for d in v.get('leaders',[]):view.leader(d)
            for t in v.get('texts',[]):view.text(t['at'],t['text'],t.get('height',2.5))
            records.append(view.finish())
        for table in record.get('tables',[]):sheet.table(table)
        for note in record.get('notes',[]):sheet.text(*note['at'],note['text'],note.get('height',2.5),max_width=note.get('width'))
        sheet.finish();print(record['id'],'rendered',flush=True)
    c.save();report=dict(solids=solids,views=records,sheets=len(spec['sheets']),manifest_sha256=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest())
    if spec.get('inspect_intersections'):
        installed=[(name,shape) for name,shape in shapes.items() if '@' in name]
        report['installed_parts']=len(installed);report['pairs_inspected']=len(installed)*(len(installed)-1)//2
        report['intersections']=[]
        for i,(a,sa) in enumerate(installed):
            for b,sb in installed[i+1:]:
                volume=sa.intersect(sb).Volume()
                if volume>1e-3:report['intersections'].append(dict(a=a,b=b,volume_mm3=volume))
    (out/'cad-audit.json').write_text(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--pdf',required=True);a=p.parse_args();build(json.loads(Path(a.input).read_text()),a.out,a.pdf)
