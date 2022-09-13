from typing import Optional, Dict, List, Union
#
# Helper objects to help with parsing the very complex metadata/details responses
#


class UserDetails:
    def __init__(self, details_obj):
        self.details_obj = details_obj

    def privileges(self) -> List[str]:
        return self.details_obj['privileges']

    def assigned_groups(self) -> List[str]:
        return self.details_obj['assignedGroups']

    def inherited_groups(self) -> List[str]:
        return self.details_obj['inheritedGroups']

    def state_of_user(self) -> str:
        return self.details_obj['state']

    def is_user_superuser(self) -> bool:
        return self.details_obj['isSuperUser']

    def user_info(self) -> Dict:
        return self.details_obj['header']

    def display_name(self) -> str:
        return self.details_obj['header']['displayName']

    def username(self) -> str:
        return self.details_obj['header']['name']

    def created_timestamp(self) -> int:
        return self.details_obj['header']['created']

    def last_modified_timestamp(self) -> int:
        return self.details_obj['header']['modified']


class GroupDetails:
    def __init__(self, details_obj):
        self.details_obj = details_obj

    def privileges(self):
        return self.details_obj['privileges']

    # Does this even make sense?
    def assigned_groups(self):
        return self.details_obj['assignedGroups']

    def inherited_groups(self):
        return self.details_obj['inheritedGroups']


class LiveboardDetails:
    def __init__(self, details_obj):
        self.details_obj = details_obj

    #
    # Not finished
    #
    def referenced_data_sources(self):
        details = self.details_obj
        # Once you get to the resolvedObjects part of the response, you have to iterate because the keys are the
        # GUIDs of each answer on the pinboard
        for ro in details["storables"][0]['header']['resolvedObjects']:
            tables = details["storables"][0]['header']['resolvedObjects'][ro]['reportContent']["sheets"][0]['sheetContent']['visualizations'][0]['vizContent']['columns'] #['column'] ## ['referencedTableHeaders']
            # can be multiple columns
            # each column may or may not have a 'column' key to get to its inner contents
            print(len(tables))
            print(tables)
