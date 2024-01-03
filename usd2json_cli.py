import os.path
import json
from pxr import Usd, UsdGeom, Gf
import sys

version_string = "v0.0.3"


def get_stage(usd_path):
    try:
        stage = Usd.Stage.Open(usd_path)
        stage.Flatten()
        return stage
    except Exception as e:
        print(e)
        return None


def check_pers_cam(_prim):
    if _prim.GetTypeName() == "Camera":
        usd_geom_cam: UsdGeom.Camera = UsdGeom.Camera(_prim)
        current_gf_camera = usd_geom_cam.GetCamera(1)
        if current_gf_camera.projection == Gf.Camera.Perspective:
            return True
    return False


def find_cameras(_stage):
    return list(filter(check_pers_cam, _stage.Traverse()))


def find_nulls(stage, cameras):
    prims = stage.Traverse()
    xforms = []
    for _prim in prims:
        pts_attr: Usd.Attribute = _prim.GetAttribute("xformOpOrder")
        if pts_attr.IsValid():
            xforms.append(_prim)

    _nulls = []
    for xform in xforms:
        # cameraの親Xformが含まれているのを外したい
        # 多分 camera と同名でカメラの親だったXformを弾けば良いはず。
        xform_name = xform.GetName()
        camera_names = list(map(lambda camera: camera.GetName(), cameras))
        if xform_name not in camera_names:
            _nulls.append(xform)

    return _nulls


def parse_camera(camera, stage):
    start_frame = stage.GetStartTimeCode()
    end_frame = stage.GetEndTimeCode()
    usd_geom_cam: UsdGeom.Camera = UsdGeom.Camera(camera)
    meter_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    fps = stage.GetFramesPerSecond()
    horizontal_aperture = []
    vertical_aperture = []
    focal_length = []
    focus_distance = []
    f_stop = []
    transform = []
    if start_frame == end_frame:
        end_frame += 1

    for current_time in range(int(start_frame), int(end_frame), 1):
        current_gf_camera = usd_geom_cam.GetCamera(current_time)
        horizontal_aperture.append(current_gf_camera.horizontalAperture)
        vertical_aperture.append(current_gf_camera.verticalAperture)
        focal_length.append(current_gf_camera.focalLength)
        focus_distance.append(current_gf_camera.focusDistance)
        f_stop.append(current_gf_camera.fStop)
        transform.append([list(current_gf_camera.transform.GetRow(0)),
                          list(current_gf_camera.transform.GetRow(1)),
                          list(current_gf_camera.transform.GetRow(2)),
                          list(current_gf_camera.transform.GetRow(3))])

    camera_data = {
        "meterPerUnit": meter_per_unit,
        "startTimeCode": start_frame,
        "endTimeCode": end_frame,
        "fps": fps,
        "name": camera.GetName(),
        "horizontalAperture": horizontal_aperture,
        "verticalAperture": vertical_aperture,
        "focalLength": focal_length,
        "focusDistance": focus_distance,
        "fStop": f_stop,
        "Xform": transform
    }
    return camera_data


def parse_null(null, stage):
    start_frame = stage.GetStartTimeCode()
    end_frame = stage.GetEndTimeCode()
    meter_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    fps = stage.GetFramesPerSecond()
    transform = []
    if start_frame == end_frame:
        end_frame += 1
    for current_time in range(int(start_frame), int(end_frame), 1):
        xform = UsdGeom.Xformable(null)
        world_transform: Gf.Matrix4d = xform.ComputeLocalToWorldTransform(current_time)
        transform.append([list(world_transform.GetRow(0)),
                          list(world_transform.GetRow(1)),
                          list(world_transform.GetRow(2)),
                          list(world_transform.GetRow(3))])

    null_data = {
        "meterPerUnit": meter_per_unit,
        "startTimeCode": start_frame,
        "endTimeCode": end_frame,
        "fps": fps,
        "name": null.GetName(),
        "Xform": transform
    }
    return null_data


def main():
    if len(sys.argv) == 1:
        print("USD file path is required")
        print("use2json_cli: " + version_string)
        return
    usd_path = sys.argv[1]
    # print(usd_path)
    stage = get_stage(usd_path)
    if stage is None:
        print("Could not open USD stage")
        print("use2json_cli: " + version_string)
        return
    cameras = find_cameras(stage)
    nulls = find_nulls(stage, cameras)
    cameras_data = []
    nulls_data = []
    for camera in cameras:
        cameras_data.append(parse_camera(camera, stage))

    for null in nulls:
        nulls_data.append(parse_null(null, stage))

    json_data = {
        "cameras": cameras_data,
        "nulls": nulls_data
    }

    json_path = os.path.splitext(usd_path)[0] + "__temp__.json"

    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(json_path)


main()
