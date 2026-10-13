# Paths resolve from this project folder, so the project can be relocated.
from pathlib import Path as _ProjectPath
import sys as _ProjectSys
_shared = str(_ProjectPath(__file__).resolve().parents[1] / 'shared')
if _shared not in _ProjectSys.path:
    _ProjectSys.path.insert(0, _shared)
from project_paths import PROJECT_ROOT, project_path

exec(compile(open(str(project_path('helpers.py')),encoding='utf-8-sig').read(),'helpers.py','exec'))
random.seed(8)
scene=bpy.data.scenes.new('Classroom | Golden Hour')
bpy.context.window.scene=scene
COLL=collection('01 Architecture',scene)
cream=mat('Walls | warm ivory',(.81,.78,.65));sage=mat('Wainscot | sage',(.25,.43,.38));white=mat('Porcelain white',(.89,.92,.92));teal=mat('Deep teal',(.025,.13,.16));navy=mat('Chair | midnight blue',(.035,.095,.15));metal=mat('Powder-coated steel',(.13,.18,.2),.35,.45);gold=mat('Brushed brass',(.56,.34,.1),.3,.65);wood=mat('Honey oak',(.56,.32,.13));chalk=mat('Chalk ivory',(.87,.9,.73));board=mat('Chalkboard',(.025,.12,.1));glass=mat('Sky glass',(.34,.69,.8),.22,.1,.25);rubber=mat('Rubber feet',(.025,.033,.04));coral=mat('Coral accents',(.8,.22,.12));paper=mat('Paper',(.94,.9,.76));leaf=mat('Leaves',(.065,.28,.16));cork=mat('Cork',(.49,.29,.12));blue=mat('Notebook blue',(.09,.32,.5));yellow=mat('Notebook mustard',(.87,.53,.08))
box('Floating foundation',(0,0,-.2),(11.1,10,.4),teal,.09)
floors=[mat('Oak floor %d'%i,(.48+i*.025,.31+i*.021,.17+i*.017)) for i in range(5)]
for row in range(25):
    y=-4.8+row*.39
    for j in range(5):
        x1=max(-5.4,-6.6+j*2.7+(row%2)*1.35);x2=min(5.4,-6.6+(j+1)*2.7+(row%2)*1.35)
        if x2>x1:box('Floorboard',((x1+x2)/2,y,.024),(x2-x1-.013,.375,.04),random.choice(floors),.009)
box('Back wall',(0,4.84,1.85),(11.1,.22,3.7),cream,.025)
box('Back sage panel',(0,4.705,.53),(10.9,.08,1.05),sage,.015)
box('Back chair rail',(0,4.62,1.06),(10.95,.095,.07),white,.015)
box('Back skirting',(0,4.62,.12),(10.95,.12,.19),white,.015)
box('Back crown',(0,4.74,3.62),(11.15,.36,.12),white)
# Three tall windows occupy the left wall.
box('Window wall lower',(-5.47,0,.55),(.22,9.7,1.1),sage)
box('Window wall lintel',(-5.47,0,3.43),(.22,9.7,.55),cream)
for y in [-4.55,-1.5,1.5,4.55]:box('Window wall pier',(-5.47,y,2.05),(.22,.62,2.0),cream)
for y in [-3.03,0,3.03]:
    box('Daylight glazing',(-5.47,y,2.12),(.045,2.4,1.93),glass,.01)
    for yy in [y-1.25,y,y+1.25]:box('Window upright',(-5.30,yy,2.12),(.14,.075,2.06),white,.012)
    for z in [1.1,2.13,3.15]:box('Window crossbar',(-5.30,y,z),(.14,2.56,.07),white,.01)
    box('Oak window sill',(-5.20,y,1.07),(.48,2.7,.1),wood)
box('Window crown',(-5.47,0,3.66),(.34,9.95,.12),white)
box('Window baseboard',(-5.29,0,.12),(.12,9.65,.19),white)
for y in [-4.4,-2.9,-1.4,.1,1.6,3.1,4.4]:box('Panel batten',(-5.31,y,.55),(.07,.065,.82),white,.007)
# Board and classroom details.
COLL=collection('02 Teaching wall',scene)
box('Chalkboard oak surround',(-.8,4.57,2.3),(6.05,.15,1.92),wood,.055)
box('Green writing surface',(-.8,4.476,2.3),(5.84,.055,1.7),board,.018)
box('Chalk tray',(-.8,4.35,1.39),(6.1,.32,.07),wood)
text('Board headline','WELCOME TO CLASS',(-3.35,4.437,2.84),.245,chalk)
text('Board lesson','EXPLORE  /  CREATE  /  DISCOVER',(-3.33,4.431,2.48),.11,chalk)
text('Board equation','a² + b² = c²',(-3.3,4.428,2.1),.22,chalk)
text('Board motto','Small questions. Big ideas.',(-3.3,4.425,1.76),.135,chalk)
line('Geometry triangle',[(.5,4.426,1.77),(1.4,4.426,1.77),(.5,4.426,2.48)],.012,chalk,True)
for i in range(4):box('Chalk stick',(-2+i*.18,4.3,1.45),(.12,.025,.025),chalk,.006)
box('Board eraser',(-.45,4.30,1.48),(.28,.13,.08),teal)
# Clock.
rod('Clock rim',(3.85,4.66,3.05),(3.85,4.51,3.05),.35,gold,n=64)
rod('Clock face',(3.85,4.505,3.05),(3.85,4.485,3.05),.307,paper,n=64)
for i in range(12):
    a=i*math.tau/12;rod('Hour mark',(3.85+.247*math.sin(a),4.46,3.05+.247*math.cos(a)),(3.85+.275*math.sin(a),4.46,3.05+.275*math.cos(a)),.009,teal,n=8)
line('Hour hand',[(3.85,4.44,3.05),(3.75,4.44,3.17)],.013,teal)
line('Minute hand',[(3.85,4.44,3.05),(4.04,4.44,3.16)],.009,teal)
box('Noticeboard surround',(3.84,4.55,1.94),(2.02,.12,1.5),wood)
box('Noticeboard cork',(3.84,4.47,1.94),(1.88,.045,1.36),cork)
text('Notice heading','THIS WEEK',(3.02,4.436,2.48),.16,paper)
for x,yz,c in [(3.30,2.05,paper),(4.21,2.03,blue),(3.35,1.58,yellow),(4.19,1.58,paper)]:
    box('Pinned note',(x,4.414,yz),(.65,.02,.38),c,.008)
    ellipsoid('Pushpin',(x,4.39,yz+.14),(.027,.022,.027),coral)
    for z in [yz+.05,yz-.03]:box('Note line',(x,4.394,z),(.42,.006,.008),teal,0)
# Furniture.
COLL=collection('03 Student desks | 16 places',scene)
for ri,y in enumerate([-3.25,-1.76,-.27,1.22]):
    for ci,x in enumerate([-3.65,-1.3,1.05,3.4]):
        prefix=f'Desk {ri+1}-{ci+1}'
        box(prefix+' | top',(x,y,.80),(1.36,.73,.09),wood,.055)
        box(prefix+' | book tray',(x,y,.62),(1.16,.60,.055),metal)
        for dx in [-.52,.52]:
            for dy in [-.24,.24]:
                rod(prefix+' | leg',(x+dx,y+dy,.09),(x+dx*.93,y+dy,.75),.028,metal)
                rod('Rubber ferrule',(x+dx,y+dy,.05),(x+dx,y+dy,.12),.037,rubber)
        cy=y-.70
        box(prefix+' | chair seat',(x,cy,.48),(.51,.49,.075),navy,.05)
        back=box(prefix+' | chair back',(x,cy-.235,.78),(.52,.075,.43),navy,.06);back.rotation_euler[0]=-.10
        for dx in [-.20,.20]:
            for dy in [-.19,.19]:rod('Chair tubular leg',(x+dx*1.13,cy+dy*1.15,.06),(x+dx,cy+dy,.46),.024,metal)
            rod('Chair back support',(x+dx,cy-.205,.28),(x+dx,cy-.27,.93),.024,metal)
        cover=random.choice([blue,coral,yellow,teal])
        book=box('Exercise book',(x-.20,y,.865),(.39,.50,.027),cover,.012);book.rotation_euler[2]=random.uniform(-.16,.16)
        box('Notebook label',(x-.2,y-.07,.883),(.20,.12,.005),paper,.004)
        rod('Pencil',(x+.18,y-.15,.864),(x+.22,y+.13,.864),.009,yellow,n=6)
        box('Desk number',(x+.47,y-.369,.80),(.14,.006,.045),paper,.004)
COLL=collection('04 Teacher area and shelves',scene)
box('Teacher desk surface',(-1.8,3.23,.89),(2.45,.94,.11),wood,.06)
for x in [-2.65,-.95]:
    box('Teacher cabinet',(x,3.23,.46),(.57,.78,.78),sage,.03)
    for z in [.29,.53,.74]:
        box('Drawer face',(x,2.824,z),(.51,.025,.18),sage,.01)
        rod('Brass drawer pull',(x-.09,2.79,z),(x+.09,2.79,z),.013,gold)
box('Teacher notebook',(-2.05,3.12,.97),(.52,.38,.05),coral)
box('Laptop base',(-1.25,3.16,.96),(.59,.39,.03),metal)
screen=box('Laptop screen',(-1.25,3.34,1.17),(.59,.035,.42),teal);screen.rotation_euler[0]=-.12
box('Laptop display',(-1.25,3.313,1.17),(.53,.008,.35),blue,.004)
rod('Pencil cup',(-2.62,3.38,.95),(-2.62,3.38,1.15),.065,paper)
for i in range(5):rod('Teacher pencil',(-2.65+i*.015,3.38,1.04),(-2.66+i*.018,3.37,1.29),.008,yellow,n=6)
# Low bookshelves along the right-hand edge.
for cx,cy in [(4.65,3.68)]:
    box('Bookcase back',(cx,cy+.21,.68),(1.20,.06,1.28),sage)
    for xx in [cx-.62,cx+.62]:box('Bookcase upright',(xx,cy,.68),(.09,.52,1.36),wood)
    for zz in [.10,.54,.98,1.36]:box('Bookcase shelf',(cx,cy,zz),(1.33,.57,.065),wood)
    for row in range(3):
        for i in range(8):
            x=cx-.51+i*.13;h=random.uniform(.25,.34)
            box('Library book',(x,cy-.04,[.10,.54,.98][row]+h/2+.04),(.09,.34,h),random.choice([blue,coral,yellow,paper,teal]),.005)
# Plants on a sill and cabinet.
def plant(x,y,z,s):
    rod('Terracotta pot',(x,y,z),(x,y,z+.25*s),.12*s,coral,r2=.18*s,n=24)
    for i in range(7):
        a=i*2.4; tip=(x+math.sin(a)*.25*s,y+math.cos(a)*.20*s,z+(.48+random.random()*.22)*s)
        rod('Plant stem',(x,y,z+.2*s),tip,.008*s,leaf)
        ob=ellipsoid('Plant leaf',tip,(.10*s,.035*s,.19*s),leaf);ob.rotation_euler=(.5*math.sin(a),.8*math.cos(a),a)
plant(-5.15,-3.0,1.14,.8);plant(4.6,3.68,1.4,.75)
# Cutaway display plaque.
box('Classroom plaque',(0,-5.02,-.18),(3.5,.06,.21),gold,.025)
text('Plaque lettering','THE CREATIVE CLASSROOM',(0,-5.058,-.23),.115,teal,'CENTER')
COLL=collection('06 Cameras and lighting',scene)
world=bpy.data.worlds.new('Warm studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.72,.88,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;scene.world=world
area('Softbox | warm key',(1,-4,10),(0,1,0),1800,(1,.84,.63),7)
area('Window light',(-7,-1,6),(-1,1,0),1500,(.74,.88,1),6)
area('Teacher rim',(2,6,7),(1,2,1),1300,(1,.74,.43),5)
sun_data=bpy.data.lights.new('Afternoon sun','SUN');sun_data.energy=1.6;sun_data.angle=.15
sun=bpy.data.objects.new('Afternoon sun',sun_data);COLL.objects.link(sun);sun.rotation_euler=(.48,-.55,-.55)
scene.camera=camera('Camera | classroom overview',(14,-18,14),(0,0,1),ortho=17.4)
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1500;scene.render.resolution_y=1320;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
scene['description']='Warm cutaway classroom, sixteen student workspaces. Original scene preserved.'
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA'
        a.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Classroom.blend'))
result={'scene':scene.name,'objects':len(scene.objects),'saved':str(ROOT/'Classroom.blend')}
