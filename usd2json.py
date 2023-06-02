import tkinter as tk
from tkinter import messagebox
import os.path
import json
from pxr import Usd, UsdGeom, Gf
from tkinterdnd2 import DND_FILES, TkinterDnD

root = TkinterDnD.Tk()
IMPORT_FILE_PATH = tk.StringVar()
CAMERA_NAME_LIST = tk.StringVar()
NULL_NAME_LIST = tk.StringVar()
export_btn: tk.Button | None = None
selected_cam_index = []
selected_null_index = []
cameras: list[UsdGeom.Camera] | None = None
nulls: list[UsdGeom.Xform] | None = None
stage: Usd.Stage | None = None


def on_drop(event):
    global IMPORT_FILE_PATH, cameras, nulls, CAMERA_NAME_LIST, NULL_NAME_LIST
    IMPORT_FILE_PATH.set(event.data)
    print('drop fileName=%s' % IMPORT_FILE_PATH.get())

    _stage = get_stage(IMPORT_FILE_PATH.get())
    if _stage:
        cameras = find_cameras(_stage)
        # noinspection PyTypeChecker
        CAMERA_NAME_LIST.set(list(map(lambda camera: camera.GetName(), cameras)))

        nulls = find_nulls(_stage)
        # noinspection PyTypeChecker
        NULL_NAME_LIST.set(list(map(lambda null: null.GetName(), nulls)))


def on_camera_select(event):
    global selected_cam_index
    selected_cam_index = list(event.widget.curselection())
    refresh_export_btn_state()


def on_null_select(event):
    global selected_null_index
    selected_null_index = list(event.widget.curselection())
    refresh_export_btn_state()


def refresh_export_btn_state():
    global selected_cam_index, selected_null_index, export_btn
    if len(selected_cam_index) + len(selected_null_index) > 0:
        export_btn['state'] = tk.NORMAL
    else:
        export_btn['state'] = tk.DISABLED


def main():
    global IMPORT_FILE_PATH, CAMERA_NAME_LIST, NULL_NAME_LIST, root, export_btn

    ####

    root.geometry("650x500")
    root.title('usd2json')
    root.drop_target_register(DND_FILES)
    root.dnd_bind(sequence="<<Drop>>", func=on_drop)

    ####

    IMPORT_FILE_PATH.set("Drop your USD file")
    tk.Label(root, text="USD file :").grid(row=0, column=0, pady=10, sticky=tk.E)
    import_file_path_label = tk.Label(root, textvariable=IMPORT_FILE_PATH)
    import_file_path_label.grid(row=0, column=1, pady=10, columnspan=99, sticky=tk.W)

    ####

    tk.Label(root, text="Cameras :").grid(row=1, column=0, sticky=tk.NE)
    camera_list_box = tk.Listbox(root, activestyle="dotbox", selectmode='extended', exportselection=False,
                                 height=5, listvariable=CAMERA_NAME_LIST)
    camera_list_box.grid(row=1, column=1, sticky=tk.EW)

    ####

    camera_list_y_bar = tk.Scrollbar(root, orient=tk.VERTICAL)
    camera_list_y_bar.grid(row=1, column=2, sticky=tk.NS)
    camera_list_y_bar.config(command=camera_list_box.yview)
    camera_list_box.config(yscrollcommand=camera_list_y_bar.set)
    camera_list_box.bind(sequence="<<ListboxSelect>>", func=on_camera_select)

    tk.Label(root, text="Nulls :").grid(row=2, column=0, sticky=tk.NE)
    null_list_box = tk.Listbox(root, activestyle="dotbox", selectmode='extended', exportselection=False,
                               listvariable=NULL_NAME_LIST)
    null_list_box.grid(row=2, column=1, sticky=tk.EW)
    null_list_y_bar = tk.Scrollbar(root, orient=tk.VERTICAL)
    null_list_y_bar.grid(row=2, column=2, sticky=tk.NS)
    null_list_y_bar.config(command=null_list_box.yview)
    null_list_box.config(yscrollcommand=null_list_y_bar.set)
    null_list_box.bind(sequence="<<ListboxSelect>>", func=on_null_select)

    ####
    export_btn = tk.Button(root, text='Export .json', command=export_json)
    export_btn["state"] = tk.DISABLED
    export_btn.grid(row=3, column=1, ipady=2, ipadx=2, padx=10, pady=10, sticky=tk.NE)

    tk.Label(root, text="").grid(row=1, column=10, padx=10, sticky=tk.E)

    root.grid_columnconfigure(1, weight=1)
    root.mainloop()


def reset_gui():
    global IMPORT_FILE_PATH, CAMERA_NAME_LIST, NULL_NAME_LIST, export_btn, stage
    IMPORT_FILE_PATH.set("Could not open USD Stage")
    # noinspection PyTypeChecker
    CAMERA_NAME_LIST.set([])
    # noinspection PyTypeChecker
    NULL_NAME_LIST.set([])
    export_btn['state'] = tk.DISABLED
    stage = None


def get_stage(usd_path):
    global stage
    try:
        stage = Usd.Stage.Open(usd_path)
        stage.Flatten()
    except Exception as e:
        print(e)
        reset_gui()

    return stage


def check_pers_cam(_prim):
    if _prim.GetTypeName() == "Camera":
        usd_geom_cam: UsdGeom.Camera = UsdGeom.Camera(_prim)
        current_gf_camera = usd_geom_cam.GetCamera(1)
        if current_gf_camera.projection == Gf.Camera.Perspective:
            return True
    return False


def find_cameras(_stage):
    return list(filter(check_pers_cam, _stage.Traverse()))


def find_nulls(_stage):
    xforms = filter(lambda _prim: _prim.GetTypeName() == "Xform", _stage.Traverse())
    _nulls = []
    for xform in xforms:
        # cameraの親Xformが含まれているのを外したい
        # 多分 camera と同名でカメラの親だったXformを弾けば良いはず。
        xform_name = xform.GetName()
        camera_names = CAMERA_NAME_LIST.get()
        if xform_name not in camera_names:
            _nulls.append(xform)

    return _nulls


def export_json():
    global IMPORT_FILE_PATH, cameras, nulls, selected_cam_index, export_btn, stage
    export_btn['state'] = tk.DISABLED

    usd_path = IMPORT_FILE_PATH.get()

    cameras_data = []
    nulls_data = []

    for cam_index, camera in enumerate(cameras):
        if cam_index in selected_cam_index:
            cameras_data.append(parse_camera(camera, stage))

    for null_index, null in enumerate(nulls):
        if null_index in selected_null_index:
            nulls_data.append(parse_null(null, stage))

    json_data = {
        "cameras": cameras_data,
        "nulls": nulls_data
    }

    json_path = os.path.splitext(usd_path)[0] + ".json"

    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    messagebox.showinfo("complete", "Exported json file.\n\n" + json_path)
    export_btn['state'] = tk.NORMAL


def parse_camera(camera: Usd.Prim, _stage: Usd.Stage):
    start_frame = _stage.GetStartTimeCode()
    end_frame = _stage.GetEndTimeCode()
    usd_geom_cam: UsdGeom.Camera = UsdGeom.Camera(camera)
    meter_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    fps = _stage.GetFramesPerSecond()
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


def parse_null(null: Usd.Prim, _stage: Usd.Stage):
    start_frame = _stage.GetStartTimeCode()
    end_frame = _stage.GetEndTimeCode()
    meter_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
    fps = _stage.GetFramesPerSecond()
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


main()
