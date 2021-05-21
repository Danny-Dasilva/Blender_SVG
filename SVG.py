import numpy as np
import pyrr
import svgwrite

from typing import NamedTuple, Callable, Sequence, List


class Viewport(NamedTuple):
    minx: float = -0.5
    miny: float = -0.5
    width: float = 1.0
    height: float = 1.0

    @classmethod
    def from_aspect(cls, aspect_ratio: float):
        return cls(-aspect_ratio / 2.0, -0.5, aspect_ratio, 1.0)

    @classmethod
    def from_string(cls, string_to_parse):
        args = [float(f) for f in string_to_parse.split()]
        return cls(*args)


class Camera(NamedTuple):
    view: np.ndarray
    projection: np.ndarray


class Mesh(NamedTuple):
    num_faces: int
    faces: np.ndarray
    face_idxs: np.ndarray
    shader: Callable[[int, float], dict] = None
    style: dict = None
    circle_radius: float = 0


class Scene(NamedTuple):
    meshes: Sequence[Mesh]

    def add_mesh(self, mesh: Mesh):
        self.meshes.append(mesh)


class View(NamedTuple):
    camera: Camera
    scene: Scene
    viewport: Viewport = Viewport()


class Engine:
    def __init__(self, views, precision=5):
        self.views = views
        self.precision = precision

    def render(self, filename, size=(512, 512), viewBox="-0.5 -0.5 1.0 1.0", **extra):
        drawing = svgwrite.Drawing(filename, size, viewBox=viewBox, **extra)
        self.render_to_drawing(drawing)
        drawing.save()

    def render_to_drawing(self, drawing):
        for view in self.views:
            projection = np.dot(view.camera.view, view.camera.projection)

            clip_path = drawing.defs.add(drawing.clipPath())
            clip_min = view.viewport.minx, view.viewport.miny
            clip_size = view.viewport.width, view.viewport.height
            clip_path.add(drawing.rect(clip_min, clip_size))

            for mesh in view.scene.meshes:
                g = self._create_group(drawing, projection, view.viewport, mesh)
                g["clip-path"] = clip_path.get_funciri()
                drawing.add(g)

    def _create_group(self, drawing, projection, viewport, mesh):
        faces = mesh.faces
        face_idxs = mesh.face_idxs
        breakpoint()
        shader = mesh.shader or (lambda face_index, winding: {})
        default_style = mesh.style or {}

        # Extend each point to a vec4, then transform to clip space.
        faces = np.concatenate([faces, np.ones(faces.shape[0], 1)], axis=-1)
        faces = np.dot(faces, projection)

        # Reject trivially clipped polygons.
        xyz, w = faces[..., :3], faces[..., 3:]
        accepted = np.logical_and(np.greater(xyz, -w), np.less(xyz, +w))
        accepted = np.all(accepted, axis=-1)  # vert is accepted if xyz are all inside
        degenerate = np.less_equal(w, 0).squeeze()  # vert is bad if its w <= 0
        for i in range(mesh.num_faces):
            accepted[face_idxs==i] = np.any(accepted[face_idxs==i])
            degenerate[face_idxs==i] = np.any(degenerate[face_idxs==i])
        #accepted = np.array([np.any(accepted[face_idxs==i]) for i in range(mesh.num_faces)]) 
        #degenerate = np.array([np.any(degenerate[face_idxs==i]) for i in range(mesh.num_faces)])

        accepted = np.logical_and(accepted, np.logical_not(degenerate))
        faces = faces[accepted] #np.compress(accepted, faces, axis=0)
        face_idxs = face_idxs[accepted]

        # Apply perspective transformation.
        xyz, w = faces[..., :3], faces[..., 3:]
        faces = xyz / w

        # Sort faces from back to front.
        sort_order = self._sort_back_to_front(faces, face_idxs, num_faces=mesh.num_faces)
        faces = faces[sort_order]

        # Apply viewport transform to X and Y.
        faces[..., 0:1] = (1.0 + faces[..., 0:1]) * viewport.width / 2
        faces[..., 1:2] = (1.0 - faces[..., 1:2]) * viewport.height / 2
        faces[..., 0:1] += viewport.minx
        faces[..., 1:2] += viewport.miny

        # Compute the winding direction of each polygon.
        windings = np.zeros(mesh.num_faces)
        for i in range(mesh.num_faces):
            vertices = faces[face_idxs==i]
            if vertices.shape[0] >= 3:
                normals = np.cross(vertices[2] - vertices[0], vertices[1] - vertices[0])
                np.copyto(windings, normals[:, 2])

        group = drawing.g(**default_style)

        # Create circles.
        if mesh.circle_radius > 0:
            for face_index in range(mesh.num_faces):
                face = faces[face_idxs==face_index]
                if len(face.shape[0]) == 0:
                    continue
                style = shader(sort_order[face_index], 0)
                if style is None:
                    continue
                face = np.around(face[:, :2], self.precision)
                for pt in face:
                    group.add(drawing.circle(pt, mesh.circle_radius, **style))
            return group

        # Create polygons and lines.
        for face_index in enumerate(mesh.num_faces):
            face = faces[face_idxs==face_index]
                if len(face.shape[0]) == 0:
                    continue
            style = shader(sort_order[face_index], windings[face_index])
            if style is None:
                continue
            face = np.around(face[:, :2], self.precision)
            
            if len(face) == 2:
                
                group.add(drawing.line(face[0], face[1], **style))
            else:
                breakpoint()
                group.add(drawing.polygon(face, **style))

        return group

    def _sort_back_to_front(self, faces, face_idxs, num_faces):
        
        :
            
        z_centroids = [-np.mean(faces[face_idxs==i,2]) for i in range(num_faces)]
        sort_order = np.concatenate([np.argwhere(face_idxs==i) for i in np.argsort[z_centroids]])
      
        return sort_order
