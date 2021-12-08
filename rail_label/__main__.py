import cv2
import pathlib

from rail_label.utils.utils import Mouse
from rail_label.utils.data_set import DataSet
from rail_label.labeling.scene import Scene


def main():
    pth = "/home/flo/mlserver/data/hofstetter_data/deleteme/measurement_2021-04-29_010/"
    data_set_path = pathlib.Path(pth)

    dataset = DataSet(data_set_path)

    # Main window
    window_name = "image"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Mouse on main window
    mouse = Mouse()
    cv2.setMouseCallback(window_name, mouse.mouse_callback)

    # Initial scene
    image = dataset[0]["image"]
    annotations = dataset[0]["annotations"]
    camera_yml = dataset[0]["camera_yml"]
    scene = Scene(image, annotations, camera_yml, mouse)

    # main loop
    data_cnt = 0
    while True:
        input_key = cv2.waitKey(1)
        if input_key == ord("q"):
            # Save scene and exit program
            dataset.write_annotations(scene.serialize())
            cv2.destroyAllWindows()
            break
        elif input_key == ord("n"):
            dataset.write_annotations(scene.serialize())
            del scene
            data_cnt += 1
            image = dataset[data_cnt]["image"]
            annotations = dataset[data_cnt]["annotations"]
            camera_yml = dataset[data_cnt]["camera_yml"]
            scene = Scene(image, annotations, camera_yml, mouse)
        elif input_key == ord("b"):
            dataset.write_annotations(scene.serialize())
            del scene
            data_cnt -= 1
            image = dataset[data_cnt]["image"]
            annotations = dataset[data_cnt]["annotations"]
            camera_yml = dataset[data_cnt]["camera_yml"]
            scene = Scene(image, annotations, camera_yml, mouse)
        elif input_key == ord("s"):
            scene.stencil_toggle()
        elif input_key == ord("d"):
            scene.stencil_correction(1)
        elif input_key == ord("a"):
            scene.stencil_correction(-1)
        elif input_key == ord("f"):
            scene.mark_point()
        elif input_key == ord("r"):
            scene.remove_point()
        elif input_key == ord("x"):
            scene.create_track("ego")
        elif input_key == ord("y"):
            scene.create_track("left")
        elif input_key == ord("c"):
            scene.create_track("right")
        elif input_key == ord("l"):
            scene.toggle_polifill()
        # Keys 0-9 represent track-ids
        elif input_key in [ord(str(zero_to_nine)) for zero_to_nine in range(10)]:
            scene.choose_track(int(chr(input_key)))
        else:
            cv2.imshow(window_name, scene.show())


if __name__ == "__main__":
    main()
