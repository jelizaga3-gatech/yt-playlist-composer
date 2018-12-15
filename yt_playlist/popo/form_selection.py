class FormItems:
    def __init__(self, item):
        if "name" not in item.keys():
            raise TypeError("Missing 'name' key.")
        elif "radio_value" not in item.keys():
            raise TypeError("Missing 'radio_value' key.")
        else:
            self.name = item["name"]
            self.radio_value = item["radio_value"]


class YouTubeItems(FormItems):
    def __init__(self, item):
        FormItems.__init__(self, item=item)
        self.item_id = item["item_id"]
        self.playlist_item_count = item["playlist_item_count"]
