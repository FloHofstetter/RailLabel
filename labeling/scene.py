import cv2
import tabulate

from labeling.stencil import Stencil
from labeling.track import Track

from utils.camera import Camera


class Scene:
    """
    Handle inputs and annotations in one image.
    """
    def __init__(self, image, annotations, camera_yml, mouse):
        """

        :param image: Image to display.
        :param annotations: Loaded annotations.
        """
        self._image = image
        self._annotations = annotations
        self._camera = Camera(camera_yml)
        self._stencil = Stencil(self._camera, mouse)
        self._tracks = {}
        if annotations is not None:
            self.unserialize(annotations)
        if not self._tracks:
            self._active_track = self.create_track("ego")
        else:
            first_track = next(iter(self._tracks.values()))
            self._activate_track(first_track.get_id())
        self._track_polifill = False


    def show(self):
        img = self._image.copy()
        img = self._stencil.draw(img).copy()
        img = self.draw_tracks(img, self._camera).copy()
        return img

    def mark_point(self):
        self._active_track.add_point(self._stencil.get_rail_points())

    def remove_point(self):
        self._active_track.remove_point(self._stencil.get_rail_points())

    def stencil_toggle(self):
        self._stencil.toggle_mode()

    def stencil_correction(self, increment):
        self._stencil.set_width_correction(increment)

    def toggle_polifill(self):
        self._track_polifill = not self._track_polifill

    def create_track(self, rel_pos):
        """
        Create new track on scene.

        :param rel_pos: Relative position to ego-track.
        :return: New track object.
        """
        new_track = Track(len(self._tracks), rel_pos)
        # Deactivate all other tracks
        [track.deactivate() for track in self._tracks.values()]
        self._tracks[new_track.get_id()] = new_track
        self._activate_track(new_track.get_id())

        return new_track

    def get_track(self, t_id):
        if t_id not in self._tracks.keys():
            msg = f"No track with id {t_id} available."
            raise ValueError(msg)
        return self._tracks[t_id]

    def _activate_track(self, t_id):
        """
        Set a track in scene active, all other are set inactive.

        :param t_id: Id of track to set active.
        :return: Activated track object.
        """
        track = self.get_track(t_id)
        # Deactivate all other tracks
        [track.deactivate() for track in self._tracks.values()]
        track.activate()
        self._active_track = track
        return track

    def choose_track(self, t_id):
        """
        Choose track to work with and handle false input.

        :param t_id: Track to work with.
        :return: Chosen track object.
        """
        try:
            track = self._activate_track(t_id)
            return track
        # Track not in dict
        except ValueError:
            msg = f"There is no track with [id: {t_id}]\n"
            msg += f"Available Tracks:"
            print(msg)
            table_headers = ["Track ID", "Rel. position"]
            table_content = []
            for track_id, track in self._tracks.items():
                table_content.append((track_id, track.get_rel_pos()))
            table = tabulate.tabulate(table_content, headers=table_headers)
            print(table)
            # If choice not available return present active track
            return self._active_track

    def draw_tracks(self, img, camera):
        """
        Draw all track on the scene.

        :return: None.
        """
        for track in self._tracks.values():
            track.draw_splines(img, 10)
        for track in self._tracks.values():
            track.draw_points(img)
        # TODO: We can do that prettier:
        for track in self._tracks.values():
            track.calculate_wire_grid_points(camera)
        for track in self._tracks.values():
            track.draw_wire_grid_points(img)
        alpha = 0.20
        img_c = img.copy()
        for track in self._tracks.values():
            track.draw_track_wire_polygon(img_c, self._track_polifill)
        img = cv2.addWeighted(img_c, alpha, img, 1 - alpha, 0)
        return img

    def serialize(self):
        """
        Serialize scene to dict.

        :return: Dict representing all annotations.
        """
        scene = {"ego track": [], "left neighbors": [], "right neighbors": []}
        for t_id, track in self._tracks.items():
            if track.get_rel_pos() == "ego":
                track_information = {
                    # "id": t_id,
                    **track.get_flat_railpoints()
                }
                scene["ego track"].append(track_information)
            elif track.get_rel_pos() == "left":
                track_information = {
                    # "id": t_id,
                    **track.get_flat_railpoints()
                }
                scene["left neighbors"].append(track_information)
            elif track.get_rel_pos() == "right":
                track_information = {
                    # "id": t_id,
                    **track.get_flat_railpoints()
                }
                scene["right neighbors"].append(track_information)
        return scene

    def unserialize(self, scene_dict):
        """

        :param scene_dict:
        :return:
        """
        scene_dict["ego"] = scene_dict.pop("ego track")
        scene_dict["left"] = scene_dict.pop("left neighbors")
        scene_dict["right"] = scene_dict.pop("right neighbors")
        for track_pos, tracks in scene_dict.items():
            for track in tracks:
                tr = self.create_track(track_pos)
                tr.add_points(track)
                tr.unflatten_flat_rails()
