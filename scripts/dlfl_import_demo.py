import os
import sys

from pytopmod.core.dlfl import obj_io
from pytopmod.core.dlfl.operations import subdivision


def main(obj_file_path: str):
    file_path, file_name = os.path.split(obj_file_path)
    file_short_name, file_ext = os.path.splitext(file_name)
    output_path = os.path.join(file_path, f"{file_short_name}_triangulated{file_ext}")

    print(f"Opening {obj_file_path}...")
    with open(obj_file_path, "r") as input_file:
        mesh = obj_io.obj_to_mesh(input_file.read())
        print(
            f"Triangulating faces.",
            f"Original mesh: faces={len(mesh.faces)} vertices={len(mesh.vertices)})",
        )
        for face in list(mesh.faces):
            subdivision.triangulate_face(mesh, face)
        print(f"Saving {output_path}...")
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(obj_io.mesh_to_obj(mesh))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(f"Usage: {sys.argv[0]} obj_file_path")
    main(sys.argv[1])
