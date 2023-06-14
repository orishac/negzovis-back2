import os, zipfile, csv


def create_disc_zip(disc_path, zip_name, files_to_zip):
    """
    This function creates a zipped file from a list of files in a desired directory
    :param disc_path: the path of the discretization
    :param zip_name: the name we want the zipped file to have in the end
    :param files_to_zip: a list of the files we want to include in the zip
    :return:
    """
    with zipfile.ZipFile(os.path.join(disc_path, zip_name), mode="w") as zipped_disc:
        for file in files_to_zip:
            file_path = os.path.join(disc_path, file)
            zipped_disc.write(file_path, os.path.basename(file_path))


def get_variable_list(path, column):
    """
    Receives a path to a raw data file and a column and extracts a list of unique values in that column
    :param data_path: a path to the raw data file
    :param column: the column which we want to get unique values from
    :return: a list of all unique value
    """
    try:
        with open(path) as data:
            variable_list = []
            reader = csv.reader(data, delimiter=",")
            for row in reader:
                variable_list.append(row[column])
            variable_list = variable_list[1:]  # truncate header
            variable_list = list(set(variable_list))  # remove duplicates
            data.close()
            return variable_list
    except (IOError, PermissionError) as e:
        raise e
