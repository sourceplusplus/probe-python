import json

import humps


class LiveSourceLocation(object):
    def __init__(self, source, line, commit_id=None, file_checksum=None):
        self.source = source
        self.line = line
        self.commit_id = commit_id
        self.file_checksum = file_checksum

    def __eq__(self, other):
        if isinstance(other, LiveSourceLocation):
            return self.source == other.source \
                   and self.line == other.line \
                   and self.commit_id == other.commit_id \
                   and self.file_checksum == other.file_checksum
        return False

    def to_json(self):
        return json.dumps(self, default=lambda o: humps.camelize(o.__dict__))

    @classmethod
    def from_json(cls, json_str):
        return LiveSourceLocation.from_dict(humps.decamelize(json.loads(json_str)))

    @classmethod
    def from_dict(cls, dict_obj):
        return LiveSourceLocation(dict_obj["source"], dict_obj["line"],
                                  dict_obj["commit_id"] if "commit_id" in dict_obj else None,
                                  dict_obj["file_checksum"] if "file_checksum" in dict_obj else None)
