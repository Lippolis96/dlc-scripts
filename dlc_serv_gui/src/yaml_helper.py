import yaml

# Reads dict from yaml file
def yaml_read_dict(path):
    file = open(path, "r")
    data = yaml.load(file)
    file.close()
    return data

# Writes dict to yaml file
def yaml_write_dict(path, data):
    file = open(path, "w")
    yaml.dump(data, file, default_flow_style=False)
    file.close()
