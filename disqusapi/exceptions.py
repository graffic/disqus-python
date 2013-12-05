class InterfaceNotDefined(NotImplementedError):
    pass


class APIError(Exception):
    def __init__(self, code, message):
        super(APIError, self).__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return '<disqusapi.APIError %s: %s>' % (self.code, self.message)


class InvalidAccessToken(APIError):
    pass


class RateLimitError(APIError):
    pass
