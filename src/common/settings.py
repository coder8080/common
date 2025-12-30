import yaml

with open("data/settings.yaml") as file:
    settings = yaml.load(file, Loader=yaml.SafeLoader)
