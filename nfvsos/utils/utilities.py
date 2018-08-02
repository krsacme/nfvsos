
def convert_to_range(cpu_list):
    if not cpu_list or '-' in cpu_list:
        return cpu_list
    if type(cpu_list) == str:
        num_list = [int(num) for num in cpu_list.split(",")]
    else:
        num_list = cpu_list
    num_list.sort()
    range_list = []
    range_min = num_list[0]
    for num in num_list:
        next_val = num + 1
        if next_val not in num_list:
            if range_min != num and (range_min + 1) != num:
                range_list.append(str(range_min) + '-' + str(num))
            else:
                range_list.append(str(range_min))
                if range_min != num:
                    range_list.append(str(num))
            next_index = num_list.index(num) + 1
            if next_index < len(num_list):
                range_min = num_list[next_index]
    return ','.join(range_list)
