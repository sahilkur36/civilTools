# import math

# import DraftVecUtils
import FreeCAD
# import Part
import Arch
import Draft


def import_model(
        etabs = None,
        import_beams : bool = True,
        import_columns : bool = True,
        import_braces : bool = True,
        import_floors : bool = True,
        import_walls : bool = True,
        new_model : bool = True,
        ):
    if etabs is None:
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
    if new_model or FreeCAD.ActiveDocument is None:
        name = etabs.get_file_name_without_suffix()
        FreeCAD.newDocument(name)
    stories_objects = {}
    etabs.set_current_unit('kgf', 'mm')
    if import_beams or import_columns or import_braces:
        profiles = {}
        frame_props = etabs.SapModel.PropFrame.GetAllFrameProperties()
        section_types_map = {
            1 : ['H', 'IPE'],
            2 : ['U', 'UNP'],
            8 : ['R', 'REC'],
            9 : ['C', 'CIRCLE'],
        }
        frames = etabs.SapModel.FrameObj.GetAllFrames()
        for i in range(frames[0]):
            # p1_name = frames[4][i]
            # p2_name = frames[5][i]
            v1 = FreeCAD.Vector(frames[6][i], frames[7][i], frames[8][i])
            v2 = FreeCAD.Vector(frames[9][i], frames[10][i], frames[11][i])
            # line = Draft.make_line((x1, y1, z1), (x2, y2, z2))
            section_name = frames[2][i]
            if section_name:
                section_index = frame_props[1].index(section_name)
                section_type_num = frame_props[2][section_index]
                section_type, category = section_types_map.get(section_type_num, ('G', 'Genaral'))
            else:
                section_type, category = 'None', 'None'
            width = frame_props[4][section_index]
            height = frame_props[3][section_index]
            profile = profiles.get(section_name, None)
            if profile is None:
                profile = Arch.makeProfile(
                    profile=[
                            0,
                            category,
                            section_name,
                            section_type,
                            width, # T3
                            height, # height
                            frame_props[6][section_index], # TW
                            frame_props[5][section_index], # TF
                            # frame_props[7][section_index], # heightB
                            # frame_props[8][section_index], # TFB
                            ])
                profiles[section_name] = profile
            profile.Label = section_name
            # edge = Part.makeLine(v1, v2)
            line = Draft.make_line(v1, v2)
            line.recompute()
            structure = Arch.makeStructure(profile)
            place_the_beam(structure, line)
            frame_name = frames[1][i]
            is_beam = is_column = is_brace = color = None
            if etabs.frame_obj.is_beam(frame_name):
                is_beam = True
                color = (1.0, 1.0, 0.0, 0.0)
            elif etabs.frame_obj.is_column(frame_name):
                is_column = True
                color = (.0, 1.0, 0.0, 0.0)
            elif etabs.frame_obj.is_brace(frame_name):
                is_brace = True
                color = (.0, 1.0, 0.0, 0.0)
            else:
                color = (1.0, 1.0, 0.0, 0.0)
            # view property of structure
            if FreeCAD.GuiUp:
                structure.ViewObject.LineWidth = 1
                structure.ViewObject.PointSize = 1
                structure.ViewObject.Transparency = 20
                if color:
                    structure.ViewObject.ShapeColor = color
                    structure.ViewObject.LineColor = color
                    structure.ViewObject.PointColor = color
                    line.ViewObject.LineColor = color
                    line.ViewObject.PointColor = color
                if section_type not in ('G', 'None'):
                    line.ViewObject.hide()
                line.ViewObject.LineWidth = 1
            
            structure.Label = frame_name
            rotation = etabs.SapModel.FrameObj.GetLocalAxes(frame_name)[0]
            insertion = etabs.SapModel.FrameObj.GetInsertionPoint(frame_name)
            x, y = get_xy_cardinal_point(insertion[0], width, height)
            if is_column:
                rotation += 90
            structure.AttachmentOffset = FreeCAD.Placement(
                FreeCAD.Vector(x, y, 0),
                FreeCAD.Rotation(FreeCAD.Vector(0,0,1),rotation))
            structure.Nodes = [v1, v2]
            story = frames[3][i]
            story_objects = stories_objects.get(story, None)
            if story_objects is None:
                stories_objects[story] = [structure]
            else:
                story_objects.append(structure)

    if import_floors or import_walls:
        (n, names, design, _, delim, _,
        x_coords, y_coords, z_coords, _) = etabs.SapModel.AreaObj.GetAllAreas()
        i = 0
        for count, j in enumerate(delim):
            xs = x_coords[i: j + 1]
            ys = y_coords[i: j + 1]
            zs = z_coords[i: j + 1]
            area = Draft.make_wire([FreeCAD.Vector(x, y, z) for x, y, z in zip(xs, ys, zs)],
                closed=True, face=True)
            area.Label = names[count]
            i = j + 1
            # View Object
            if FreeCAD.GuiUp:
                design_type = design[count]
                if design_type == 1:  # wall
                    color = (1., 0., 0.)
                elif design_type == 2: # floor
                    color = (.8, .8, .8)
                elif design_type == 4:
                    area.ViewObject.DisplayMode = "Wireframe"
                area.ViewObject.ShapeColor = color
                area.ViewObject.LineColor = color
                area.ViewObject.PointColor = color
                area.ViewObject.LineWidth = 1
                area.ViewObject.PointSize = 1
                area.ViewObject.Transparency = 40

    # create IFC objects
    floors = make_building(etabs)
    for f in floors:
        name = f.Label
        f.Group = stories_objects.get(name, [])
    FreeCAD.ActiveDocument.recompute()

def make_building(etabs):
    ret = etabs.SapModel.Story.GetStories()
    floors = []
    for i in range(ret[0] + 1):
        f = Arch.makeFloor([], name=ret[1][i])
        f.Placement.Base.z = ret[2][i]
        f.Height = ret[3][i]
        floors.append(f)
    # building = Arch.makeBuilding(floors)
    # site = Arch.makeSite([building])
    # Arch.makeProject([site])
    return floors

def place_the_beam(beam, line):
    '''arg1= beam, arg2= edge: lay down the selected beam on the selected edge'''
    edge = line.Shape.Edges[0]
    vect=edge.tangentAt(0)
    beam.Placement.Rotation=FreeCAD.Rotation(0,0,0,1)
    rot=FreeCAD.Rotation(beam.Placement.Rotation.Axis,vect)
    beam.Placement.Rotation=rot.multiply(beam.Placement.Rotation)
    beam.Placement.Base=edge.valueAt(0)
    beam.addExtension("Part::AttachExtensionPython")
    beam.Support=[(line, 'Edge1')]
    beam.MapMode='NormalToEdge'
    beam.MapReversed=True
    beam.Height=edge.Length

def get_xy_cardinal_point(
        cardinal : int,
        width : float,
        height : float,
        ):
    x = y = 0
    if cardinal in (1, 4, 7):
        x = width / 2
    elif cardinal in (3, 6, 9):
        x = - width / 2
    if cardinal in (7, 8, 9):
        y = - height / 2
    elif cardinal in (1, 2, 3):
        y = height / 2
    return x, y

def get_xyz_offset(insertion : list):
    x1, y1, z1 = insertion[3]
    x2, y2, z2 = insertion[4]
    x += (x1 + x2) / 2
    y += (y1 + y2) / 2
    z = (z1 + z2) / 2
    return x, y, z
