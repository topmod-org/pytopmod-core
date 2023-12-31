from pytopmod.core.dlfl import obj_io, primitives
from pytopmod.core.dlfl.operations import subdivision


def main():
    with open("dlfl_triangle.obj", "w", encoding="utf-8") as f:
        f.write(obj_io.mesh_to_obj(primitives.triangle()))

    mesh = primitives.tetrahedron()
    with open("dlfl_tetrahedron.obj", "w", encoding="utf-8") as f:
        f.write(obj_io.mesh_to_obj(mesh))

    print("Subdividing tetrahedron...")
    for _ in range(10):
        for face_key in list(mesh.face_keys):
            subdivision.triangulate_face(mesh, face_key)
    print(f"Done. Faces={len(mesh.face_keys):_}, Vertices={len(mesh.vertex_keys):_}")
    with open("dlfl_tetrahedron_subdivided.obj", "w", encoding="utf-8") as f:
        f.write(obj_io.mesh_to_obj(mesh))


if __name__ == "__main__":
    main()
