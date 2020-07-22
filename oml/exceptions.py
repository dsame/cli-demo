class OMLException(Exception):
    """Base exception in OML"""
    def __init__(self, msg, *args, **kwargs):
        if isinstance(msg, str):
            msg += '\n\nYou can check the FAQ section in our docs for common issues ' \
                'and how to solve them: https://aka.ms/oxooml?anchor=faq'
        super().__init__(msg, *args, **kwargs)
