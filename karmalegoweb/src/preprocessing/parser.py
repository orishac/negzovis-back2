from karmalegoweb.src.manage_data.kl_output import get_params, get_tirps_names, read_tirp
from karmalegoweb.src.preprocessing.tim_parsed import entity, tim, tirp, instance


def parse(kl_id, cls=None) -> tim:
    tim = parse_params(kl_id, cls)
    tim.tirps = [
        parse_tirp_file(kl_id, cls, tirp_name) for tirp_name in get_tirps_names(kl_id, cls)
    ]
    return tim


def parse_params(kl_id, cls) -> tim:
    params_line = get_params(kl_id, cls)
    params_line = params_line[:-1]
    params = dict([tuple(name_value.split("=")) for name_value in params_line.split(";")])

    return tim(
        input_path=params["time_intervals_path"],
        min_ver_support=float(params["min_ver_support"]),
        num_relations=params["num_relations"],
        max_gap=params["max_gap"],
        label=params["label"],
        epsilon=params["epsilon"],
        output_path=params["output_path"],
        incremental_output=params["incremental_output"],
        max_tirp_length=params["max_tirp_length"],
        num_comma=params["num_comma"],
        symbol_type=params["symbol_type"],
        skip_followers=params["skip_followers"],
        entity_ids_num=params["entity_ids_num"],
        index_same=params["index_same"],
        semicolon_end=params["semicolon_end"],
        need_one_sized=params["need_one_sized"],
        selected_variables=params["selected_variables"],
        calc_offsets=params["calc_offsets"],
        print_instances=params["print_instances"],
        print_params=params["print_params"],
        filter_overlapping_grad_state=params["filter_overlapping_grad_state"],
        num_of_entities=int(params["num_of_entities"]),
    )


def parse_tirp_file(kl_id, cls, tirp_name) -> tirp:
    tirps_params_line, data_lines = read_tirp(kl_id, cls, tirp_name)
    data_lines = list(map(lambda s: s[:-1], data_lines))
    entities_lines_start = data_lines.index("\\(^0_0^)/")
    instances_lines = data_lines[:entities_lines_start]
    entities_lines = data_lines[entities_lines_start + 1 :]

    tirp = parse_tirp_metrics(tirps_params_line)
    entities = parse_entities(entities_lines)
    instances = parse_instances(instances_lines)
    for instance in instances:
        entities[instance.entity_id].instances.append(instance)

    tirp.entities = entities
    return tirp


def parse_tirp_metrics(line: str) -> tirp:
    line = line.split(" ")
    line = line[1:]  # deletes the '#' in the beginning

    size = line[0]
    symbols = line[1].split("-")[:-1]
    relations = [] if line[2] == "" else line[2].split(".")[:-1]
    mean_duration = line[3]
    mean_offset_start = line[4]
    mean_offset_end = line[5]
    vertical_support = line[6]
    mean_horizontal_support = line[7].split("\n")[0]
    return tirp(
        size=int(size),
        symbols=symbols,
        relations=relations,
        vertical_support=int(vertical_support),
        mean_horizontal_support=float(mean_horizontal_support),
        mean_duration=float(mean_duration),
        mean_offset_from_start=float(mean_offset_start),
        mean_offset_from_end=float(mean_offset_end),
    )


def parse_entities(windows_lines):
    entities = {}
    for window_line in windows_lines:
        [entity_id, stats] = window_line.split(":")
        [window_times, mean_duration, mean_offset_start, mean_offset_end] = stats.split(" ")
        [window_start, window_end] = window_times[1:-1].split("-")
        entities[entity_id] = entity(
            entity_id,
            float(window_start),
            float(window_end),
            float(mean_duration),
            float(mean_offset_start),
            float(mean_offset_end),
        )

    return entities


def parse_instances(entities_lines: list) -> list:
    instances = []
    for entity_line in entities_lines:
        [entity_id, instances_line] = entity_line.split(":")
        instances_str = instances_line.split(";")

        for instance_str in instances_str:
            instance_parameters = instance_str.split(" ")

            intervals_str = instance_parameters[0]
            intervals = [tuple(interval.split("-")) for interval in intervals_str.split(",")]
            intervals = [(float(start), float(end)) for start, end in intervals]

            duration = instance_parameters[1]
            offset_from_start = instance_parameters[2]
            offset_from_end = instance_parameters[3]

            current_instance = instance(
                entity_id=entity_id,
                intervals=intervals,
                duration=float(duration),
                offset_from_start=float(offset_from_start),
                offset_from_end=float(offset_from_end),
            )

            instances.append(current_instance)
    return instances
