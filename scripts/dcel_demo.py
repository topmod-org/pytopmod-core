from pytopmod.core.dcel import obj_io, primitives


def main():
    with open("dcel_triangle.obj", "w", encoding="utf-8") as f:
        f.write(obj_io.mesh_to_obj(primitives.triangle()))

    mesh = primitives.tetrahedron()
    with open("dcel_tetrahedron.obj", "w", encoding="utf-8") as f:
        f.write(obj_io.mesh_to_obj(mesh))


if __name__ == "__main__":
    main()
