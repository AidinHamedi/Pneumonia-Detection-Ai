# Copyright (c) 2024 Aydin Hamedi
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# start L1>>>
print("Loading the GUI...", end="\r")
# Import Sys level
import os
import traceback
import sys
import tkinter as tk
from tkinter import messagebox

# Try to import main GUI lib
try:
    import PySimpleGUI as sg
except (ImportError, NameError):
    print("Failed to load PySimpleGUI lib | Exiting")
    with open("Data\\logs\\SYS_FAILED_START_LOG.log", "a") as log_file:
        log_file.write(f"\n<L1> Failed to load PySimpleGUI lib Tr({traceback.format_exc()})</L1>\n")
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Internal Error | Exiting", "Failed to import PySimpleGUI, exiting...")
    sys.exit()
# prep GUI
sg.theme("GrayGrayGray")
# Start
sg.popup_auto_close(
    "┌──────────┐\n      Loading...    \n└──────────┘",
    non_blocking=True,
    auto_close_duration=3,
    no_titlebar=True,
    line_width=32,
    button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
    font=(None, 14, "bold"),
)
# pylib
try:
    # import re # noqa: F401
    import time
    import cv2
    import gzip
    import json
    import base64
    import atexit
    import queue
    import hashlib
    import pydicom
    import cpuinfo

    # import difflib # noqa: F401
    # import inspect # noqa: F401
    import traceback
    import subprocess
    import threading
    import requests
    import numpy as np
    from tqdm import tqdm

    # from time import sleep # noqa: F401
    from loguru import logger
    from tkinter import filedialog
    from datetime import datetime
    from PIL import Image
    import tensorflow as tf
    from keras.models import load_model
    from requests.exceptions import RequestException, ConnectionError

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    # Utils
    from Utils.Grad_cam import make_gradcam_heatmap
    from Utils.print_color_V2_NEW import print_Color_V2  # noqa: F401
    from Utils.print_color_V1_OLD import print_Color
    from Utils.FixedDropout import FixedDropout
except (ImportError, NameError):
    print("Failed to load the GUI libs")
    print("detailed error message:")
    traceback.print_exc()
    with open("Data\\logs\\SYS_FAILED_START_LOG.log", "a") as log_file:
        log_file.write("\n<L2> Failed to load the GUI libs </L2>\n")
        log_file.write(f"<L2> Traceback:\n{traceback.format_exc()}</L2>\n")
    sg.popup(
        f"An internal error occurred.\nERROR-INFO:\n\nFailed to load the GUI python libs.\n\nErr-Traceback:\n{traceback.format_exc()}",
        title="Internal Error | Exiting",
        custom_text=("Exit"),
    )
    sys.exit()
# global vars>>>
# CONST SYS
GUI_Ver = "0.9.6"
Model_dir = "Data/PAI_model"  # without file extention
Database_dir = "Data/dataset.npy"
IMG_AF = ("JPEG", "PNG", "BMP", "TIFF", "JPG", "DCM", "DICOM")
Github_repo_Releases_Model_info_name = "model_info.json"
Github_repo_Releases_URL = "https://api.github.com/repos/Aydinhamedi/Pneumonia-Detection-Ai/releases/latest"
Model_FORMAT = "H5_SF"  # TF_dir/H5_SF
IMG_RES = (224, 224, 3)
Debug_m = False
# normal global
available_models = []
img_array = None
label = None
model = None


# Other
class CustomQueue:
    # Custom queue class with size limit
    #
    # Initializes a Queue instance with a max size. Provides put(), get(),
    # and is_updated() methods to add items, retrieve items, and check if
    # updated since last get() call.
    def __init__(self, max_items=4):
        self.q = queue.Queue()
        self.max_items = max_items
        self.is_updated = False

    def put(self, item):
        if self.q.qsize() == self.max_items:
            self.q.get()
        self.q.put(item)
        self.is_updated = True

    def get(self, reset_updated=True):
        items = list(self.q.queue)
        if reset_updated:
            self.is_updated = False
        return items

    def is_updated(self):
        return self.is_updated


# GUI_Data
GUI_Queue = {"-Main_log-": CustomQueue(max_items=128)}
logger.remove()
logger.add("Data\\logs\\SYS_LOG_{time}.log", backtrace=True, diagnose=True, compression="zip")
logger.info("GUI Start...\n")
tf.get_logger().setLevel("ERROR")
physical_devices = tf.config.list_physical_devices("GPU")
for gpu_instance in physical_devices:
    tf.config.experimental.set_memory_growth(gpu_instance, True)
# Making the GUI layout >>>
# Main
GUI_layout_Tab_main = [
    [sg.Text("Enter the image dir:", font=(None, 10, "bold"))],
    [
        sg.Input(key="-INPUT_IMG_dir-", enable_events=True, size=(48, 1)),
        sg.Button("Browse", key="-BUTTON_BROWSE_IMG_dir-"),
    ],
    [sg.Text("Log:", font=(None, 10, "bold"))],
    [sg.Multiline(key="-OUTPUT_ST-", size=(54, 6), autoscroll=True, disabled=True, write_only=True)],
    [sg.Text("Result:", font=(None, 10, "bold"))],
    [sg.Text(key="-OUTPUT_ST_R-", size=(50, 2), background_color="white")],
    [
        sg.Checkbox("Show Grad-CAM", key="-CHECKBOX_SHOW_Grad-CAM-", default=True),
        sg.Checkbox("Show DICOM Info", key="-CHECKBOX_SHOW_DICOM_INFO-", default=True),
    ],
    [sg.Button("Analyse"), sg.Button("Close")],
]
# Ai Model
GUI_layout_Tab_Ai_Model = [
    [sg.Text("Ai Model Settings:", font=(None, 10, "bold"))],
    [
        sg.Button("Update/Download Model", key="-BUTTON_UPDATE_MODEL-"),
        sg.Button("Reload Model", key="-BUTTON_RELOAD_MODEL-"),
    ],
    [
        sg.Table(
            "",
            key="-TABLE_ST_MODEL-",
            headings=["Avaialble Models"],
            enable_events=True,
            enable_click_events=True,
            justification="left",
            selected_row_colors="gray",
            col_widths=[40],
            num_rows=3,
        )
    ],
    [sg.Text("Ai Model Info:", font=(None, 10, "bold"))],
    [sg.Text(key="-OUTPUT_Model_info-", size=(40, 7), pad=(4, 0))],
]
# Sys info
GUI_layout_Tab_Sys_Info = [
    [sg.Text("System Info:", font=(None, 10, "bold"))],
    [
        sg.Multiline("N/A", key="-OUTPUT_ST_SYS_INFO-", size=(54, 8), expand_y=True, disabled=True, write_only=True),
    ],
]


# DICOM Info
def C_GUI_layout_DICOM_Info_Window() -> list:
    """Returns the layout for the DICOM Info tab.

    This consists of a single Multiline element to display the DICOM metadata.

    Returns:
        list: The layout as a list of rows.
    """
    return [
        [
            sg.Multiline(
                key="-OUTPUT_DICOM_Info-",
                size=(120, 40),
                font=(None, 11, "normal"),
                autoscroll=True,
            )
        ]
    ]


# GUI logo
GUI_text_logo = """
~*
  _______  __    __   __     .___  ___.   ______    _______   _______ 
 /  _____||  |  |  | |  |    |   \\/   |  /  __  \\  |       \\ |   ____|
|  |  __  |  |  |  | |  |    |  \\  /  | |  |  |  | |  .--.  ||  |__   
|  | |_ | |  |  |  | |  |    |  |\\/|  | |  |  |  | |  |  |  ||   __|  
|  |__| | |  `--'  | |  |    |  |  |  | |  `--'  | |  '--'  ||  |____ 
 \\______|  \\______/  |__|    |__|  |__|  \\______/  |_______/ |_______|
~*                                                                      
  ______   .__   __.                                                  
 /  __  \\  |  \\ |  |                                                  
|  |  |  | |   \\|  |                                                  
|  |  |  | |  . `  |                                                  
|  `--'  | |  |\\   |                                                  
 \\______/  |__| \\__|                                                  
                          
"""


# HF>>>
# calculate_file_hash
def calculate_file_hash(file_path) -> str:
    """Calculates a SHA256 hash for the contents of the given file.

    Args:
        file_path (str): The path to the file to hash.

    Returns:
        str: The hex string of the SHA256 hash.
    """
    with open(file_path, "rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest()
    return readable_hash


# get_model_info
def get_model_info(model_path) -> dict:
    """Gets information about a model file.

    Checks if the model file exists at the given path, calculates its hash,
    and looks up version information in a JSON file if it exists.

    Args:
        model_path: Path to the model file.

    Returns:
        Dict with file hash, whether it exists, version, and model type.
    """

    # Check if the model exists
    model_exists = os.path.exists(model_path)

    if model_exists:
        # Calculate the hash of the file
        file_hash = calculate_file_hash(model_path)

        # Load the JSON data
        with open("Data/model_info.json", "r") as json_file:
            model_info = json.load(json_file)

        # Check if the file's hash is in the JSON data
        if file_hash in model_info:
            # Return the 'Ver' and 'stored_type' attributes for the file
            return {
                "file_hash": file_hash,
                "file_exists": True,
                "Ver": model_info[file_hash]["Ver"],
                "stored_type": model_info[file_hash]["stored_type"],
            }
        else:
            return {
                "file_hash": file_hash,
                "file_exists": True,
                "Ver": "Unknown",
                "stored_type": "Unknown",
            }
    else:
        return {
            "file_hash": "Unknown",
            "file_exists": False,
            "Ver": "Unknown",
            "stored_type": "Unknown",
        }


# open_file_GUI
def open_file_GUI() -> str:
    """Opens a file selection dialog GUI to allow the user to select an image file.

    Builds a filetypes filter from the IMG_AF global variable, joins the extensions
    together into a filter string, converts to lowercase. Opens the file dialog,
    and returns the selected file path if one was chosen.

    Returns:
        str: The path to the selected image file, or None if no file was chosen.
    """
    formats = ";*.".join(IMG_AF)
    formats = "*." + formats.lower()
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", formats)])
    if file_path:
        return file_path


# get_latest_release_files
def get_latest_release_files(url) -> list:
    """Fetches information about the latest release assets from the GitHub API.

    Args:
    url (str): The URL of the GitHub repository API endpoint

    Returns:
    None

    Prints the names of the files included in the latest release of the GitHub
    repository specified by the URL. Makes a GET request to the URL, checks if
    the request was successful, parses the JSON response, extracts the assets
    from the latest release, and prints the name of each asset file. If the request
    fails, prints an error message with the status code.
    """
    assets = []
    # Make a GET request to the GitHub API
    try:
        response = requests.get(url)
    except (ConnectionError, RequestException):
        print("Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection)")
        GUI_Queue["-Main_log-"].put(
            "Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection)"
        )
        logger.warning(
            f"get_latest_release_files>>ERROR: Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection) Tr({traceback.format_exc()})"
        )
        return assets

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Debug out
        compressed_data = gzip.compress(str(data).encode())
        compressed_base64 = base64.b64encode(compressed_data).decode()
        logger.debug(f"get_latest_release_files:data(json/gzip/base64) ~Gzip_Base64[{compressed_base64}]Gzip_Base64~")
        # You can decompress it like --> gzip.decompress(base64.b64decode(compressed_base64)).decode()
        # Extract the assets from the latest release
        assets_temp = data["assets"]
        assets = [asset["name"] for asset in assets_temp]
        # Print the names of the files in the latest release
        return assets
    else:
        print(f"Failed to fetch the latest release. Status code: {response.status_code}")
        GUI_Queue["-Main_log-"].put(f"Failed to fetch the latest release. Status code: {response.status_code}")
        return assets


# download_file_from_github
def download_file_from_github(url: str, file_name: str, save_as: str, chunk_size: int) -> None:
    """Downloads a file from a GitHub release API URL to a local path.

    Args:
        url (str): The GitHub API URL for the release to download from.
        file_name (str): The name of the file to download from the release.
        save_as (str): The local path to save the downloaded file to.
        chunk_size (int): The chunk size to use when streaming the download.
    """
    # Make a GET request to the GitHub API
    try:
        response = requests.get(url)
    except (ConnectionError, RequestException):
        print("Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection)")
        GUI_Queue["-Main_log-"].put(
            "Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection)"
        )
        logger.warning(
            f"download_file_from_github>>ERROR: Failed to make a GET request to the GitHub API (Possible Cause: Max requests exceeded / Broken internet connection) Tr({traceback.format_exc()})"
        )
        raise Exception
    data = response.json()
    # Debug out
    compressed_data = gzip.compress(str(data).encode())
    compressed_base64 = base64.b64encode(compressed_data).decode()
    logger.debug(f"download_file_from_github:data(json/gzip/base64) ~Gzip_Base64[{compressed_base64}]Gzip_Base64~")
    # You can decompress it like --> gzip.decompress(base64.b64decode(compressed_base64)).decode()
    # Get the name of the latest release
    release_name = data["name"]
    print(f"Latest release: {release_name}")
    GUI_Queue["-Main_log-"].put(f"Latest Github repo release: {release_name}")
    # Get the assets of the latest release
    assets = data["assets"]

    # Find the required asset in the assets
    for asset in assets:
        if asset["name"] == file_name:
            download_url = asset["browser_download_url"]
            break
    if "download_url" in locals():
        # Download the file with a progress bar
        response = requests.get(download_url, stream=True)
        file_size = int(response.headers["Content-Length"])
        progress_bar = tqdm(total=file_size, unit="b", unit_scale=True)

        with open(save_as, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                progress_bar.update(len(chunk))
                f.write(chunk)

        progress_bar.close()

        if file_size != 0 and progress_bar.n != file_size:
            print_Color(
                "~*ERROR: ~*Something went wrong while downloading the file.",
                ["red", "yellow"],
                advanced_mode=True,
            )
            GUI_Queue["-Main_log-"].put("ERROR: Something went wrong while downloading the file.")
            logger.warning("download_file_from_github>>ERROR: Something went wrong while downloading the file.")
            raise Exception
        else:
            print(f'File "{save_as}" downloaded successfully.')
            logger.debug(f'download_file_from_github>>Debug: File "{save_as}" downloaded successfully.')
    else:
        print_Color(
            "~*ERROR: ~*Something went wrong while finding the file.",
            ["red", "yellow"],
            advanced_mode=True,
        )
        GUI_Queue["-Main_log-"].put("ERROR: Something went wrong while finding the file.")
        logger.warning("download_file_from_github>>ERROR: Something went wrong while finding the file.")
        raise Exception


# CF>>>
# Ai_Predict
def Ai_Predict(show_gradcam: bool = True) -> str:
    """
    Ai_Predict predicts pneumonia from an input image using a pre-trained deep learning model.

    It loads the model if not already loaded, runs prediction, computes confidence score
    and class name. Optionally displays GradCAM visualization heatmap.

    Returns:
        str: Prediction result string with class name, confidence score and warnings.
    """
    # global var import
    global model
    # check for input img
    if img_array is not None:
        try:
            if model is None:
                print_Color("loading the Ai model...", ["normal"])
                model = load_model(Model_dir, custom_objects={"FixedDropout": FixedDropout})
        except (ImportError, IOError):
            logger.warning(f"Ai_Predict>>ERROR: Failed to load the model. Tr({traceback.format_exc()})")
            return "ERROR: Failed to load the model."
        else:
            print_Color("predicting with the Ai model...", ["normal"])
            model_prediction_ORG = model.predict(img_array)
            model_prediction = np.argmax(model_prediction_ORG, axis=1)
            pred_class = "PNEUMONIA" if model_prediction == 1 else "NORMAL"
            confidence = np.max(model_prediction_ORG)
            return_temp = f"the Ai model prediction: {pred_class} with confidence {confidence:.2f}."
            if confidence < 0.82:
                return_temp += "WARNING: the confidence is low."
            if model_prediction == 1 and show_gradcam:
                clahe = cv2.createCLAHE(clipLimit=1.8)
                Grad_cam_heatmap = make_gradcam_heatmap(
                    img_array,
                    model,
                    "top_activation",
                    second_last_conv_layer_name="top_conv",
                    sensitivity_map=2,
                    pred_index=tf.argmax(model_prediction_ORG[0]),
                )
                Grad_cam_heatmap = cv2.resize(
                    np.clip(Grad_cam_heatmap, 0, 1),
                    (img_array.shape[1], img_array.shape[2]),
                )
                Grad_cam_heatmap = np.uint8(255 * Grad_cam_heatmap)
                Grad_cam_heatmap = cv2.applyColorMap(Grad_cam_heatmap, cv2.COLORMAP_VIRIDIS)
                Grad_cam_heatmap = np.clip(
                    np.uint8((Grad_cam_heatmap * 0.3) + ((img_array * 255) * 0.7)),
                    0,
                    255,
                )
                # Resize the heatmap for a larger display
                display_size = (600, 600)  # Change this to your desired display size
                Grad_cam_heatmap = cv2.resize(Grad_cam_heatmap[0], display_size)
                reference_image = np.uint8(cv2.resize(img_array[0] * 255, display_size))
                # Apply the CLAHE algorithm to the reference image
                reference_image_CLAHE = np.clip(
                    clahe.apply(cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)),
                    0,
                    255,
                )
                # Display the heatmap in a new window
                cv2.imshow("Grad-CAM Heatmap", Grad_cam_heatmap)
                cv2.imshow("Reference Original Image", reference_image)
                cv2.imshow("Reference Original Image (CLAHE)", reference_image_CLAHE)
            return return_temp
    else:
        print_Color(
            "~*ERROR: ~*image data doesnt exist.",
            ["red", "yellow"],
            advanced_mode=True,
            return_str=True,
        )


# reload_model
def reload_model() -> None:
    """Loads the AI model on startup.

    Tries to load the model from the Model_dir path. If successful, logs a message to the GUI queue. If loading fails, logs an error.
    """
    # global var import
    global model
    # main proc
    model = None
    GUI_Queue["-Main_log-"].put("loading the Ai model...")
    try:
        model = load_model(Model_dir, custom_objects={"FixedDropout": FixedDropout})
    except (ImportError, IOError):
        GUI_Queue["-Main_log-"].put("ERROR: Failed to load the model.")
        logger.warning(f"reload_model>>ERROR: Failed to load the model. Tr({traceback.format_exc()})")
        return None
    GUI_Queue["-Main_log-"].put("loading the Ai model done.")


# load_image
def load_image(img_dir, Show_DICOM_INFO: bool = True) -> str:
    """Loads an image from the given image file path into a numpy array for model prediction.

    Supports JPEG, PNG and DICOM image formats. Resizes images to the model input shape, normalizes pixel values,
    adds batch dimension, and provides optional DICOM metadata output.

    Args:
        img_dir: File path of image to load.
        Show_DICOM_INFO: Whether to output DICOM metadata to GUI window.

    Returns:
        Status message string indicating if image was loaded successfully.

    """
    # global var import
    global img_array
    # check for img
    logger.debug(f"load_image:img_dir {img_dir}")
    # Extract file extension from img_dir
    try:
        _, file_extension = os.path.splitext(img_dir)
    except TypeError:
        logger.warning("load_image>>ERROR: Invalid file format. Please provide an image file. (Extension Extractiion Failed)")
        return "ERROR: Invalid file format. Please provide an image file. (Extension Extractiion Failed)"
    if file_extension.upper()[1:] not in IMG_AF:
        logger.warning("load_image>>ERROR: Invalid file format. Please provide an image file.")
        return "ERROR: Invalid file format. Please provide an image file."
    else:
        try:
            # Load and resize the image
            if file_extension.upper()[1:] in ["DICOM", "DCM"]:
                ds = pydicom.dcmread(img_dir)
                img = Image.fromarray(ds.pixel_array).resize(IMG_RES[:2])
                if Show_DICOM_INFO:
                    GUI_layout_DICOM_Info_Window_layout = C_GUI_layout_DICOM_Info_Window()
                    GUI_layout_DICOM_Info_Window = sg.Window(
                        "DICOM Info - File Metadata",
                        GUI_layout_DICOM_Info_Window_layout,
                        finalize=True,
                    )
                    # Write DICOM info to the window
                    for element in ds:
                        if element.name != "Pixel Data":
                            tag_info = f"[Tag: {element.tag} | VR: {element.VR}]"
                            name_info = f"(Name: {element.name})"
                            value_info = f">Value: {element.value}"
                            GUI_layout_DICOM_Info_Window["-OUTPUT_DICOM_Info-"].print(tag_info, text_color="blue", end="")
                            GUI_layout_DICOM_Info_Window["-OUTPUT_DICOM_Info-"].print(name_info, text_color="green", end="")
                            GUI_layout_DICOM_Info_Window["-OUTPUT_DICOM_Info-"].print(value_info, text_color="black", end="\n")
                    GUI_layout_DICOM_Info_Window.finalize()
            else:
                img = Image.open(img_dir).resize((IMG_RES[1], IMG_RES[0]))
        except (NameError, FileNotFoundError):
            logger.warning("load_image>>ERROR: Invalid file dir. Please provide an image file.")
            return "ERROR: Invalid file dir. Please provide an image file."
        else:
            # Check for RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")
            # Convert to numpy array
            img_array = np.asarray(img)

            # Normalize pixel values to [0, 1]
            img_array = img_array / 255.0

            # Add a dimension to transform from (height, width, channels) to (batch_size, height, width, channels)
            img_array = np.expand_dims(img_array, axis=0)

            return "Image loaded."


# download_model
def download_model(model_type_id) -> None:
    """Downloads the model from GitHub releases.

    Handles logging status messages to the GUI queue and any errors.
    """
    try:
        GUI_Queue["-Main_log-"].put(f"Downloading model {available_models[model_type_id[0]][0]}...")
        download_file_from_github(
            Github_repo_Releases_URL,
            available_models[model_type_id[0]][0],
            Model_dir,
            1024,
        )
        reload_model()
        print("Model downloaded.")
    except Exception:
        GUI_Queue["-Main_log-"].put("ERROR: Failed to download the model.")
        logger.warning(f"download_model>>ERROR: Failed to download the model. Tr({traceback.format_exc()})")
    else:
        GUI_Queue["-Main_log-"].put("Model downloaded.")


# download_model_info
def download_model_info() -> None:
    """Downloads the model info JSON file from GitHub releases.

    Handles logging status messages to the GUI queue and any errors.
    The model info file contains metadata about the model version.
    """
    try:
        download_file_from_github(
            Github_repo_Releases_URL,
            Github_repo_Releases_Model_info_name,
            "Data\\model_info.json",
            256,
        )
    except Exception:
        GUI_Queue["-Main_log-"].put("ERROR: Failed to download the model info.")
        logger.warning(f"download_model_info>>ERROR: Failed to download the model info. Tr({traceback.format_exc()})")
    else:
        GUI_Queue["-Main_log-"].put("Model info downloaded.")


# model_info
def model_info() -> str:
    if not os.path.isfile("Data\\model_info.json") or time.time() - os.path.getmtime("Data/model_info.json") > 4 * 60 * 60:
        download_model_info()
    model_info_dict = get_model_info(Model_dir)
    if model_info_dict["Ver"] != "Unknown":
        Model_State = "OK"
    elif model_info_dict["Ver"] == "Unknown" and model_info_dict["file_exists"]:
        Model_State = "Model is not a valid model. (hash not found!)"
    else:
        Model_State = "Model file is missing."
    model_info_str = f'File_exists: {str(model_info_dict["file_exists"])}\n'
    model_info_str += f'Model_hash (SHA256): {model_info_dict["file_hash"].strip()}\n'
    model_info_str += f'stored_type: {model_info_dict["stored_type"]}\n'
    model_info_str += f"State: {Model_State}\n"
    model_info_str += f'Ver: {model_info_dict["Ver"]}'
    return {"model_info_str": model_info_str}


# funcs(INTERNAL)>>>
# IEH
def IEH(id: str = "Unknown", stop: bool = True, DEV: bool = True) -> None:
    """Prints an error message, logs the exception, optionally shows the traceback, and optionally exits.

    This is an internal error handler to nicely handle unexpected errors and optionally exit gracefully.
    """
    print_Color(
        f"~*ERROR: ~*Internal error info/id:\n~*{id}~*.",
        ["red", "yellow", "bg_red", "yellow"],
        advanced_mode=True,
    )
    logger.exception(f"Internal Error Handler [stop:{stop}|DEV:{DEV}|id:{id}]")
    if DEV:
        sg.popup(
            f"An internal error occurred.\nERROR-INFO:\n\nErr-ID:\n{id}\n\nErr-Traceback:\n{traceback.format_exc()}",
            title=f"Internal Error Exit[{stop}]",
            custom_text=("Exit"),
        )
        print_Color("detailed error message:", ["yellow"])
        traceback.print_exc()
    if stop:
        logger.warning("SYS EXIT|ERROR: Internal|by Internal Error Handler")
        sys.exit("SYS EXIT|ERROR: Internal|by Internal Error Handler")


# _Exit
@atexit.register
def _Exit():
    GUI_window_CE = ""
    try:
        GUI_window.close()
    except Exception as err:
        GUI_window_CE = err
    if Debug_m:
        print("! <Exit handler> Exiting app...")
        print(f"! <Exit handler> GUI close err: [{GUI_window_CE}]")
        print("! <Exit handler> Global var dump:")
        for var in globals().items():
            print(f"! <Exit handler> -<G dump>- {var[0]} --> {var[1]}")
        print("! <Exit handler> Exited app.")


# UWL
def UWL(Only_finalize: bool = False) -> None:
    """Updates the GUI window.

    This is an internal function to update the GUI window.
    """
    # Update the GUI window
    GUI_window.read(timeout=0)
    if GUI_Queue["-Main_log-"].is_updated and not Only_finalize:
        # Retrieve the result from the queue
        result_expanded = ""
        result = GUI_Queue["-Main_log-"].get()
        print(f"Queue Data: {result}")
        logger.debug(f"Queue:get: {result}")
        # Update the GUI with the result message
        for block in result:
            result_expanded += f"> {block}\n"
        GUI_window["-OUTPUT_ST-"].update(result_expanded, text_color="black")
    GUI_window.finalize()


# main
def main() -> None:
    """Main function for the GUI."""
    # start
    # sg.SystemTray.notify("Pneumonia-Detection-Ai-GUI", f"Gui started.\nV{GUI_Ver}")
    if Debug_m:
        sg.SystemTray.notify(
            "Pneumonia-Detection-Ai-GUI", f"Looks like you are a programmer\nWow.\nV{GUI_Ver}", icon=sg.SYSTEM_TRAY_MESSAGE_ICON_WARNING
        )
        sg.show_debugger_window()
    # global
    global GUI_window
    global available_models
    global release_files
    # Text print
    print_Color(GUI_text_logo, ["yellow", "green"], advanced_mode=True)
    # prep var
    IMG_dir = None
    Update_model_info_LXT = None
    Update_release_files_LXT = None
    # Create the tabs
    GUI_tab_main = sg.Tab("Main", GUI_layout_Tab_main)
    GUI_tab_Ai_model = sg.Tab("Ai Model", GUI_layout_Tab_Ai_Model)
    GUI_tab_Sys_info = sg.Tab("System Info", GUI_layout_Tab_Sys_Info)
    GUI_layout_group = [[sg.TabGroup([[GUI_tab_main, GUI_tab_Ai_model, GUI_tab_Sys_info]])]]
    # Create the window
    GUI_window = sg.Window(f"Pneumonia-Detection-Ai-GUI V{GUI_Ver}", GUI_layout_group, finalize=True)
    # Pre up
    download_model_info()
    # Prep GUI sys info
    GUI_window["-OUTPUT_ST_SYS_INFO-"].update(GUI_Info)
    # Main loop for the Graphical User Interface (GUI)
    while True:
        # Read events and values from the GUI window
        event, values = GUI_window.read(timeout=100, timeout_key="-TIMEOUT-")
        if not event == "-TIMEOUT-":
            logger.debug(f"GUI_window:event: {event}")
            logger.debug(f"GUI_window:values: {values}")
            print(f"GUI_window:event: ~e[{event}]e~\n")
            print(f"GUI_window:values: ~v[{values}]v~\n")

        # Check if the window has been closed or the 'Close' button has been clicked
        if event == sg.WINDOW_CLOSED or event == "Close":
            # close GUI_window
            GUI_window.close()
            # try to stop the download_model_Thread
            # try:
            #     download_model_Thread.()
            # except Exception:
            #     pass
            break  # Exit the loop and close the window

        # Handle event for updating the model
        if event == "-BUTTON_RELOAD_MODEL-":
            # Call the function to reload the model
            reload_model()

        # Handle event for browsing and selecting an image directory
        if event == "-BUTTON_BROWSE_IMG_dir-":
            # Open file dialog to select an image, and update the input field with the selected directory
            IMG_dir = open_file_GUI()
            GUI_window["-INPUT_IMG_dir-"].update(IMG_dir)

        # Handle event for confirming the selected image directory
        if event == "-INPUT_IMG_dir-":
            # Retrieve the image directory from the input field and update the display
            IMG_dir = GUI_window["-INPUT_IMG_dir-"].get()
            GUI_window["-INPUT_IMG_dir-"].update(IMG_dir)

        # Handle event for analyzing the selected image
        if event == "Analyse":
            # Call the function to load the image and update the output status
            Log_temp_txt = load_image(IMG_dir, Show_DICOM_INFO=values["-CHECKBOX_SHOW_DICOM_INFO-"])
            GUI_Queue["-Main_log-"].put(Log_temp_txt)
            UWL()

            # If the image is successfully loaded, proceed with analysis
            if Log_temp_txt == "Image loaded.":
                GUI_Queue["-Main_log-"].put("Analyzing...")
                UWL()
                # Call the function to perform pneumonia analysis and display the results
                Log_temp_txt2 = Ai_Predict(show_gradcam=values["-CHECKBOX_SHOW_Grad-CAM-"])
                logger.info(f"Ai_Predict: {Log_temp_txt2}")
                GUI_Queue["-Main_log-"].put("Done Analyzing.")
                UWL()
                GUI_window["-OUTPUT_ST_R-"].update(
                    Log_temp_txt2,
                    text_color="green" if "NORMAL" in Log_temp_txt2 else "red",
                    background_color="white",
                )
                UWL()

        # Handle event for updating the AI model
        if event == "-BUTTON_UPDATE_MODEL-":
            # Start a new thread to download the model without freezing the GUI
            if values["-TABLE_ST_MODEL-"] == []:
                GUI_Queue["-Main_log-"].put("ERROR: Failed to download the model. Select a available model from the list.")
            else:
                download_model_Thread = threading.Thread(target=download_model, args=(values["-TABLE_ST_MODEL-"],), daemon=True)
                download_model_Thread.start()
        # Updating the model info + ...
        if Update_release_files_LXT is None or time.time() - Update_release_files_LXT > 1 * 60 * 60:
            Update_release_files_LXT = time.time()
            release_files = get_latest_release_files(Github_repo_Releases_URL)
            for model_name in release_files:
                if model_name.split(".")[1] == "h5" and not model_name.__contains__("weights"):
                    available_models.append([model_name])

        if Update_model_info_LXT is None or time.time() - Update_model_info_LXT > 15:
            Update_model_info_LXT = time.time()
            Github_repo_Release_info = model_info()
            GUI_window["-OUTPUT_Model_info-"].update(Github_repo_Release_info["model_info_str"], text_color="black")
            GUI_window["-TABLE_ST_MODEL-"].update(available_models)
            UWL(Only_finalize=True)
        # Continuously check if there are results in the queue to be processed '-Main_log-'
        if GUI_Queue["-Main_log-"].is_updated:
            # Retrieve the result from the queue
            result_expanded = ""
            result = GUI_Queue["-Main_log-"].get()
            print(f"Queue Data: {result}\n")
            logger.debug(f"Queue[-Main_log-]:get: {result}")
            # Update the GUI with the result message
            for block in result:
                result_expanded += f"> {block}\n"
            GUI_window["-OUTPUT_ST-"].update(result_expanded, text_color="black")
            UWL()


# start>>>
# clear the 'start L1' prompt
print("                  ", end="\r")
# Start INFO
VER = f"V{GUI_Ver}" + datetime.now().strftime(" | CDT(%Y/%m/%d | %H:%M:%S)")
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    TF_MODE = "GPU"
    TF_sys_details = tf.sysconfig.get_build_info()
    TF_CUDA_VER = TF_sys_details["cuda_version"]
    TF_CUDNN_VER = TF_sys_details["cudnn_version"]  # NOT USED
    try:
        gpu_name = subprocess.check_output(["nvidia-smi", "-L"]).decode("utf-8").split(":")[1].split("(")[0].strip()
        # GPU 0: NVIDIA `THE GPU NAME` (UUID: GPU-'xxxxxxxxxxxxxxxxxxxx')
        #     │                       │
        # ┌---┴----------┐        ┌---┴----------┐
        # │.split(':')[1]│        │.split('(')[0]│
        # └--------------┘        └--------------┘
    except Exception:
        gpu_name = "\x1b[0;31mNVIDIA-SMI-ERROR\x1b[0m"
    TF_INFO = f"GPU NAME: {gpus[0].name}>>{gpu_name}, CUDA Version: {TF_CUDA_VER}"
else:
    TF_MODE = "CPU"
    info = cpuinfo.get_cpu_info()["brand_raw"]
    TF_INFO = f"{info}"
# GUI_Info
GUI_Info = f"PDAI Ver: {VER} \nPython Ver: {sys.version} \nTensorflow Ver: {tf.version.VERSION}, Mode: {TF_MODE}, {TF_INFO}"
logger.info(f"PDAI Ver: {VER}")
logger.info(f"Python Ver: {sys.version}")
logger.info(f"Tensorflow Ver: {tf.version.VERSION}")
logger.info(f"Mode: {TF_MODE}, {TF_INFO}")
print(GUI_Info)
# FP
if Model_FORMAT not in ["TF_dir", "H5_SF"]:
    logger.info(f"Model file format [{Model_FORMAT}]")
    IEH(id="F[SYS],P[FP],Error[Invalid Model_FORMAT]", DEV=False)
elif Model_FORMAT == "H5_SF":
    Model_dir += ".h5"
# start main
if __name__ == "__main__":
    try:
        try:
            main()
        except (EOFError, KeyboardInterrupt):
            logger.info("KeyboardInterrupt.")
            pass
    except Exception as e:
        IEH(id=f"F[SYS],RFunc[main],Error[{e}]", DEV=True)
    else:
        logger.info("GUI Exit.")
        print_Color("\n~*[PDAI GUI] ~*closed.", ["yellow", "red"], advanced_mode=True)
else:
    logger.info("GUI Imported.")
# end(EOF)
