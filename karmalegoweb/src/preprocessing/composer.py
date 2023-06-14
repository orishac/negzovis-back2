from karmalegoweb.src.preprocessing.tim_parsed import tim, entity, instance, tirp


def compose(interface: tim) -> str:
    first_params_line = compose_first_params_line(interface=interface)
    final_str = first_params_line + "\n"
    final_str += compose_tirps(interface.tirps)
    return final_str


def compose_tirps(tirps: list) -> str:
    tirps_str = ""
    for tirp in tirps:
        tirp_str = compose_tirp(tirp)
        tirps_str += tirp_str + "\n"
    return tirps_str


def compose_first_params_line(interface: tim) -> str:
    first_params_line = f"time_intervals_path={interface.input_path};min_ver_support={interface.min_ver_support};num_relations={interface.num_relations};"
    first_params_line += f"max_gap={interface.max_gap};label={interface.label};epsilon={interface.epsilon};output_path={interface.output_path};"
    first_params_line += f"incremental_output={interface.incremental_output};max_tirp_length={interface.max_tirp_length};num_comma={interface.num_comma};"
    first_params_line += f"symbol_type={interface.symbol_type};skip_followers={interface.skip_followers};entity_ids_num={interface.entity_ids_num};"
    first_params_line += f"index_same={interface.index_same};semicolon_end={interface.semicolon_end};need_one_sized={interface.need_one_sized};"
    first_params_line += f"selected_variables={interface.selected_variables};calc_offsets={interface.calc_offsets};print_instances={interface.print_instances};"
    first_params_line += f"print_params={interface.print_params};filter_overlapping_grad_state={interface.filter_overlapping_grad_state};"
    first_params_line += f"num_of_entities={interface.num_of_entities};"
    return first_params_line


def compose_tirp(tirp: tirp) -> str:
    tirp_metrics_instances_str = compose_metrics_instances(tirp)
    tirp_windows_str = compose_tirp_entities(tirp)
    return tirp_metrics_instances_str + "\n" + tirp_windows_str


def compose_metrics_instances(tirp: tirp) -> str:
    tirp_metrics_str = f"{tirp.size} {symbols_to_str(tirp.symbols)} {relations_to_str(tirp.relations)} {tirp.mean_duration} {tirp.mean_offset_from_start} "
    tirp_metrics_str += (
        f"{tirp.mean_offset_from_end} {tirp.vertical_support} {tirp.mean_horizontal_support} "
    )
    tirp_metrics_str += f"{compose_entities_instances(tirp)}"
    return tirp_metrics_str


def compose_entities_instances(tirp: tirp) -> str:
    entities_instances_str = ""
    instances = []
    for entity in tirp.entities.values():
        for instance in entity.instances:
            entities_instances_str += compose_instance_intervals(instance) + " "
    return entities_instances_str


def compose_tirp_entities(tirp: tirp) -> str:
    entities_str = ""
    for entity in tirp.entities.values():
        entities_str += compose_entity(entity) + ", "
    entities_str = entities_str[:-2]
    return entities_str


def compose_entity(entity: entity) -> str:
    window_str = f"{entity.id}, [{entity.window_start}, {entity.window_end}]: {entity.mean_duration} {entity.mean_offset_from_start} {entity.mean_offset_from_end}"
    return window_str


def compose_instance_intervals(instance: instance) -> str:
    entity_str = f"{str(instance.entity_id)} {intervals_to_str(instance.intervals)} {str(instance.duration)} "
    entity_str += f"{str(instance.offset_from_start)} {str(instance.offset_from_end)}"
    return entity_str


def intervals_to_str(intervals_arr) -> str:
    intervals_str = ""
    for interval in intervals_arr:
        intervals_str += f"[{int(interval[0])}-{int(interval[1])}]"
    return intervals_str


def symbols_to_str(symbols) -> str:
    symbols_str = ""
    for symbol in symbols:
        symbols_str += str(symbol) + "-"
    return symbols_str


def relations_to_str(relations) -> str:
    relations_str = ""
    for relation in relations:
        relations_str += relation + "."
    return relations_str
