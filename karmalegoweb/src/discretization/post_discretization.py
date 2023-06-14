import os, sys

import pandas as pd


def validate_file_creation(path):
    """
    Validates the existence of files in a certain path.
    :param path: the path that contains all of our files
    :param list_of_files: a list of files we want to make sure are in the path
    :return: True if all files exist, False otherwise
    """
    mandatory_files = [
        # "entity-class-relations.csv",
        # "prop-data.csv",
        # "symbolic-time-series.csv",
        "states.csv",
        "KL.txt",
    ]

    flag = True
    for file in mandatory_files:
        flag &= os.path.exists(os.path.join(path, file))
    return flag


def name_bins(dataset_path, disc_path, request_files_names, is_per_property, binsNames):
    vmap_path = os.path.join(dataset_path, "VMap.csv")
    states_path = os.path.join(disc_path, "states.csv")
    states_gradient_path = os.path.join(disc_path, "states_kb_gradient.csv")
    vmap_df = pd.read_csv(vmap_path)
    
    if "GradientFile" in request_files_names:
        df = pd.read_csv(states_gradient_path)
    else:
        df = pd.read_csv(states_path)

    df["TemporalPropertyName"] = "random"

    def add_name_to_df(row):
        filtered_rows = vmap_df[vmap_df["Variable ID"] == row["TemporalPropertyID"]]
        name = list(filtered_rows["Variable Name"])[0]
        row["TemporalPropertyName"] = name
        return row

    df = df.apply(add_name_to_df, axis=1)
    if ("GradientFile" in request_files_names):
        df.to_csv(states_gradient_path, index=False)
    else:
        df.to_csv(states_path, index=False)

    if (
        "KnowledgeBasedFile" not in request_files_names
        and not is_per_property
    ):
        bins_names = binsNames.split(",")

        def add_bins_names_to_df(row):
            bin_name = bins_names[int(row['BinID']) % len(bins_names)]
            if bin_name == "":
                row["BinLabel"] = row["BinID"]
            else:
                row["BinLabel"] = bin_name
            return row

        df = df.apply(add_bins_names_to_df, axis=1)
        if ("GradientFile" in request_files_names):
            df.to_csv(states_gradient_path, index=False)
        else:
            df.to_csv(states_path, index=False)
            
def process_kl_input(disc_path):
    for filename in os.listdir(disc_path):
        if filename.endswith(".txt"):
            kl_input_path = os.path.join(disc_path, filename)
            kl_processed_input = filename.replace(".txt", "_processed.txt")
            kl_processed_input_path = os.path.join(disc_path, kl_processed_input)
            __parse_kl_input(kl_input_path, kl_processed_input_path)

            os.remove(kl_input_path)
            os.rename(kl_processed_input_path, kl_input_path)


def __parse_kl_input(input_path, output_path):
    """
    This function performs necessary processing on the KarmaLego input
    in order for it to be understood by the KLW system.
    :param input_path: the input path to the file
    :param output_path: the path to the processed file
    :return:
    """
    index = 0
    file = open(input_path, "r+")
    t = open(output_path, "w")
    t.write(file.readline())  # startConcepts
    t.write(file.readline())  # numberOfEntities
    entity_id_line = file.readline()
    while entity_id_line:
        entity_details_line = file.readline()
        var_min, var_max = __find_max_and_min(entity_details_line)
        entity_id_line = (
            entity_id_line[0 : entity_id_line.index(";")]
            + ","
            + str(index)
            + ";"
            + var_min
            + ";"
            + var_max
            + "\n"
        )
        t.write(entity_id_line)
        t.write(entity_details_line)
        entity_id_line = file.readline()
        index += 1
    file.close()


def __find_max_and_min(line):
    """
    this is a helper function that finds the min and max values in an array
    :param line: in witch lins to for
    :return: the min and max values
    """
    var_min = sys.maxsize
    var_max = -sys.maxsize
    line_arr = line.split(";")
    for sec in line_arr:
        sec_arr = sec.split(",")
        if len(sec_arr) != 4:
            continue
        start_time = int(sec_arr[0])
        if start_time < var_min:
            var_min = start_time
        end_time = int(sec_arr[1])
        if end_time > var_max:
            var_max = end_time
    return str(0), str(var_max)
