#!/usr/bin/env python3

import fnmatch
import hashlib
import os
import re
import datetime
import json


flags = {"DRY_RUN": False, "DRY_PRINT": False}


out_folder = "Output"
in_folder = "Input"


def create_new_file_name(timestamp):
    dt_object = datetime.datetime.utcfromtimestamp(timestamp)

    formatted_name = dt_object.strftime("%Y%m%d_%H%M%S")

    return formatted_name


def str_to_int_timestamp(timestamp_str):
    # TODO doc string

    try:
        timestamp_int = int(timestamp_str)
    except:
        raise ValueError(
            f"Timestamp '{timestamp_str}'"
            "cannot be interpreted as an integer."
        )

    if timestamp_int < 0:
        raise ValueError("Timestamp is too small.")

    if timestamp_int > 4294967295:
        raise ValueError("Timestamp is too big.")

    return timestamp_int


def get_timestamp_str(json_file_path):
    """

    TODO rewrite this

    retrieves the deployment id from a json file, and returns it as a string.

    Opens file in read mode, parses its contents as json data, retrieves the
    deployment id and returns it.

    Args:
        id_file_path (str): The full path of the json file that contains the
                            deployment id.

    Raises:
        KeyError: Raised when "id" is not found in the json file.
        Exception: Raised when the file cant be found or opened.
        Exception: Raised when the json data can not be parsed properly.

    Returns:
        str: The timestamp that the photo was taken.
    """
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
            taken_timestamp = data["photoTakenTime"]["timestamp"]
            if taken_timestamp is None:
                raise KeyError("timestamp not found in JSON data")

            return taken_timestamp

    except (FileNotFoundError, IOError) as e:
        raise Exception(
            f"Error occurred while opening or reading JSON file: {e}"
        )
    except json.JSONDecodeError as e:
        raise Exception(f"Error occurred while parsing JSON: {e}")


def add_extension(file_name_extensionless, file_type):
    """
    Adds a specific file_type extension to a file name.

    Args:
        file_name_extensionless (str): The name of the file (with no file type
                                       specified)
        file_type (str): The type of file, with no dot.

    Returns:
        str: the combined file name and type
    """
    return file_name_extensionless + "." + file_type


def get_file_extension(file_name):
    return os.path.splitext(file_name)[-1].lower()[1:]


def get_file_base_name(file_name):
    return os.path.splitext(file_name)[0].lower()


def get_hash(path):
    with open(path, "rb") as file:
        # Read file as bytes
        bytes = file.read()

        # Calculate the MD5 Hash value of the file.
        MD5_hash = hashlib.md5(bytes).hexdigest()
        file.close()

    return MD5_hash


def do_thing(file_name):
    has_live_photo = False

    file_base_name = get_file_base_name(file_name)

    file_extension = get_file_extension(file_name)

    live_photo_file_name = file_base_name + ".MP4"

    if os.path.isfile(live_photo_file_name) and (file_extension != "mp4"):
        has_live_photo = True

    # Get the name of the companying JSON file
    JSON_file_name = add_extension(file_name, "json")

    pattern = r"\(\d+\)"  # Matches a digit or more between brackets
    match = re.search(pattern, file_name)
    if match:
        dupe_indicator = match.group(0)
        with_no_dupe = re.sub(pattern, "", file_name)
        JSON_file_name = with_no_dupe + dupe_indicator + ".json"

    if os.path.isfile(JSON_file_name):
        # From the JSON file, get the date that the image was created
        timestamp_str = get_timestamp_str(JSON_file_name)

        if not flags["DRY_RUN"]:
            os.remove(JSON_file_name)
        else:
            if flags["DRY_PRINT"]:
                print(
                    "Dry run mode: Would have removed '" + JSON_file_name + "'"
                )

        timestamp = str_to_int_timestamp(timestamp_str)

        # Inject this date into the metadata of the image file
        if not flags["DRY_RUN"]:
            os.utime(file_name, (timestamp, timestamp))
            if has_live_photo:
                os.utime(live_photo_file_name, (timestamp, timestamp))
        else:
            if flags["DRY_PRINT"]:
                # Convert the timestamp to datetime object
                dt_object = datetime.datetime.fromtimestamp(timestamp)

                # Format the datetime object into a string
                formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                print(
                    "Dry run mode: Would have updated file modified time to "
                    + formatted_time
                )

    else:
        return

    timestamp = os.path.getmtime(file_name)

    new_file_name = add_extension(
        create_new_file_name(timestamp), file_extension
    )
    new_file_path = out_folder + "\\" + new_file_name

    dupe = 0
    counter = 1
    while os.path.exists(new_file_path):
        current_MD5_hash = get_hash(file_name)
        target_MD5_hash = get_hash(new_file_path)

        if current_MD5_hash == target_MD5_hash:
            dupe = 1
            break

        # Generate the new file name with an incrementing counter
        file_name_half, file_extension_half = os.path.splitext(new_file_path)
        new_file_path = f"{file_name_half}({counter}){file_extension_half}"
        counter += 1
        # TODO fix that a 2nd dupe is getting listed as (1)(2) not just (2)

    if dupe == 0:
        if not flags["DRY_RUN"]:
            os.rename(file_name, new_file_path)
            if has_live_photo:
                os.rename(live_photo_file_name, new_file_path + ".live")
        else:
            if flags["DRY_PRINT"]:
                print(
                    "Dry run mode: would have renamed removed '"
                    + file_name
                    + "' to '"
                    + new_file_name
                    + "'"
                )

    if flags["DRY_PRINT"]:
        print("")

    # os.remove(file_name)
    # compare two

    # if they match just disregard the file

    # if they dont match increase the counter

    # counter = 1
    # while os.path.exists(new_file_path):
    #     # Generate the new file name with an incrementing counter
    #     file_name_half, file_extension_half = os.path.splitext(file_name)
    #     new_file_path = f"{file_name_half}({counter}){file_extension_half}"
    #     counter += 1

    # print("Renaming ",file_name,"to", new_file_path)
    # os.rename(file_name, new_file_path)


def iterate(folder_path):
    # Iterate through all files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if not fnmatch.fnmatch(file_name, "*.json"):  # Exclude JSON files
                file_path = os.path.join(root, file_name)
                # Process the file or perform any desired operations
                do_thing(file_path)  # Example: Print the file path


# Main function
def main():
    iterate(in_folder)

    # read_metadata(file_name)

    # a_file = filedate.File(file_name)

    # print(a_file.set(modified = "2022.01.01 14:00:00"))


# Execute the main function
if __name__ == "__main__":
    exit_code = 0
    try:
        main()
    except Exception as e:
        print(e)
        exit_code = 1

    exit(exit_code)
