import ctypes


def delete_objects(object_list: list):
    for object in object_list:
        object.delete_instance()


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
