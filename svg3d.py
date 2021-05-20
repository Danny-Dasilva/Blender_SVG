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
        shader = mesh.shader or (lambda face_index, winding: {})
        default_style = mesh.style or {}

        # Extend each point to a vec4, then transform to clip space.
        faces = np.concatenate([faces, np.ones(faces.shape[0], 1)], axis=1)
        faces = np.dot(faces, projection)

        # Reject trivially clipped polygons.
        xyz, w = faces[:, :, :3], faces[:, :, 3:]
        accepted = np.logical_and(np.greater(xyz, -w), np.less(xyz, +w))
        accepted = np.all(accepted,  axis=-1)  # vert is accepted if xyz are all inside
        accepted[]# are any of the vertices are accepted the face is accepted
        accepted = np.any(accepted, 1)  # face is accepted if any vert is inside
        degenerate = np.less_equal(w, 0)[:, :, 0]  # vert is bad if its w <= 0
        degenerate = np.any(degenerate, 1)  # face is bad if any of its verts are bad
        accepted = np.logical_and(accepted, np.logical_not(degenerate))
        faces = faces[accepted]

        # Apply perspective transformation.
        xyz, w = faces[:, :, :3], faces[:, :, 3:]
        faces = xyz / w

        # Sort faces from back to front.
        face_indices = self._sort_back_to_front(faces)
        faces = faces[face_indices]

        # Apply viewport transform to X and Y.
        faces[:, :, 0:1] = (1.0 + faces[:, :, 0:1]) * viewport.width / 2
        faces[:, :, 1:2] = (1.0 - faces[:, :, 1:2]) * viewport.height / 2
        faces[:, :, 0:1] += viewport.minx
        faces[:, :, 1:2] += viewport.miny

        # Compute the winding direction of each polygon.
        windings = np.zeros(faces.shape[0])
        if faces.shape[1] >= 3:
            p0, p1, p2 = faces[:, 0, :], faces[:, 1, :], faces[:, 2, :]
            normals = np.cross(p2 - p0, p1 - p0)
            np.copyto(windings, normals[:, 2])

        group = drawing.g(**default_style)

        # Create circles.
        if mesh.circle_radius > 0:
            for face_index, face in enumerate(faces):
                style = shader(face_indices[face_index], 0)
                if style is None:
                    continue
                face = np.around(face[:, :2], self.precision)
                for pt in face:
                    group.add(drawing.circle(pt, mesh.circle_radius, **style))
            return group

        # Create polygons and lines.
        for face_index, face in enumerate(faces):
            style = shader(face_indices[face_index], windings[face_index])
            if style is None:
                continue
            face = np.around(face[:, :2], self.precision)
            
            if len(face) == 2:
                
                group.add(drawing.line(face[0], face[1], **style))
            else:
                
                group.add(drawing.polygon(face, **style))

        return group

    def _sort_back_to_front(self, faces):
        
        z_centroids = -np.mean(faces[:, :, 2], axis=1)
      
        return np.argsort(z_centroids)
