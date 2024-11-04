def delete_objects(object_list: list):
    for object in object_list:
        object.delete_instance()
