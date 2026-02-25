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

def config(filename = '/home/medic/djangoproject/semds_errors/database.ini', section = 'postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}

    if parser.has_section(section):
        params = parser.items(section)

        for param in params:
            db[param[0]] = param[1]

    else:

        raise Exception(f'Section {section} not found in the {filename} file') 

    return db
#print(get_config_data('telegram_bot'))