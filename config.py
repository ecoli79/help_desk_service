from configparser import ConfigParser

file_config = './config.ini'

def get_config_data(section, filename=file_config):
    parser = ConfigParser()
    parser.read(filename)
    config_data = {}
    
    try:
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                config_data[param[0]] = param[1]
        return config_data
    except Exception:
        return(Exception)
