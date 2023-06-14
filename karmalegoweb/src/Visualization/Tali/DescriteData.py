import json
from operator import index
import os
from flask import current_app
import re

class DescriteData:

    def __init__(self):

        self.dataset_to_lines = {}
        self.range = {}

    def parse_descrite_data(self, dataset_name,id_number,visualizationid):
        visualization_path = os.path.join(
            current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid
        )
        
        if self.dataset_to_lines.get((dataset_name,visualizationid),-1) == -1:
            class0_lines = self.get_lines_from_file(visualization_path, "KLOutput_class0")
            lines_dictionary, range = self.lines_to_dictionary(class0_lines)
            self.dataset_to_lines[(dataset_name,visualizationid)] = lines_dictionary
            self.range[(dataset_name,visualizationid)] = range
            return lines_dictionary[int(id_number)], range
        else:
            return self.dataset_to_lines[(dataset_name,visualizationid)][int(id_number)], self.range[(dataset_name,visualizationid)]

        # class1_path = os.path.join(visualization_path, "KLOutput_class1")
        # if path.exists(class1_path):  # read lines from class 1 only if exists
        #     class1_lines, calc_offsets_class1 = get_lines_from_file(
        #         visualization_path, "KLOutput_class1"
        #     )
        # else:
        #     class1_lines = None

    def lines_to_dictionary(self, lines):
        dic = {}
        index = 0
        current_id = 1
        start_end = []
        for line in lines:
            if index%2 == 0:
                line_splitted = line.split(";")
                entity_id = line_splitted[0].split(",")[0]
                dic[int(entity_id)] = {}
                current_id = int(entity_id)
                if len(start_end)== 0:
                    start = line.split(";")[1]
                    end = line.split(";")[2]
                    start_end= [int(start),int(end)]
            if index%2 == 1:
                line_splitted = line.split(";")[:-1]
                entity_dict = dic[int(current_id)]
                for interval in line_splitted:
                    interval_data = interval.split(",")
                    if entity_dict.get(int(interval_data[2]),-1) == -1:
                        entity_dict[int(interval_data[2])] = [[int(interval_data[0]),int(interval_data[1])]]
                    else:
                        entity_dict[int(interval_data[2])].append([int(interval_data[0]),int(interval_data[1])])
            index+=1

        return dic, start_end

    def get_lines_from_file(self,visualization_path, kl_name):
        path = os.path.join(visualization_path, kl_name)
        myfile = open(path)
        lines = []
        for line in myfile:
            lines.append(line.rstrip("\n"))
        # first line is just karma-lego output parameters
        first_line = lines[0]
        all_params = re.split(";", first_line)
        params = list(map(lambda param_line: param_line.split("="), all_params))
        intervals_path = ""
        for parameter in params:
            if parameter[0] == "time_intervals_path":
                intervals_path = parameter[1]
                break
        lines = []
        if intervals_path != "":
            index_row = 0
            with open(intervals_path,"r") as file:
                for line in file:
                    if index_row == 0 or index_row == 1:
                        index_row +=1
                        continue
                    stripped_line = line.strip()
                    lines.append(stripped_line)
                    index_row +=1
            return lines
        return lines

