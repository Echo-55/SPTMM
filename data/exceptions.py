class MissingProfileJson(Exception):
    """Raised when the profile.json file is missing."""

    def __init__(
        self,
        message="The profile.json file is missing.",
        profile_json=None,
        selected_version=None,
    ):
        self.message = message
        super().__init__(
            f'\n\n{self.message}\nVersion: {selected_version}\nPath in config="{profile_json}"\nMake sure the path in config.ini is correct and the file exists.'
        )
