import json
from flask import Response

# Global Variables
MASON = "application/vnd.mason+json"
LINK_RELATIONS_URL = "https://bookingmanagementsystem1.docs.apiary.io/#reference/link-relations"
PRODUCT_PROFILE = "/profiles/product/"
ERROR_PROFILE = "/profiles/error/"


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class Utils(object):

    @staticmethod
    def create_error_response(status_code=None, title=None, message=None, path=None):
        resource_url = path
        body = MasonBuilder(resource_url=resource_url)
        body.add_error(title, message)
        body.add_control("profile", href=ERROR_PROFILE)
        return Response(json.dumps(body), status_code, mimetype=MASON)


#utility class for User model to create metadata
class UserItemBuilder(MasonBuilder):

    @staticmethod
    def product_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "user's name",
            "type": "string"
        }
        return schema

    def add_control_edit_user(self, userID, url):
        self.add_control("edit", method="PUT", href=url,
                         encoding="json", schema=self.product_schema())

    def add_control_delete_user(self, userID, url):
        self.add_control("delete", method="DELETE", href=url,
                         encoding="json")

    def add_control_add_user(self, url):
        self.add_control("bookingmeta:add-user", method="POST", href=url,
                         encoding="json", schema=self.product_schema())

    def add_control_get_all_bookables(self, userID, url):
        self.add_control("bookingmeta:all-bookables", method="GET", href=url,
                         title="Bookables collection of a User")

    def add_control_get_sent_request(self, userID, url):
        self.add_control("bookingmeta:sent-requests", method="GET", href=url,
                         title="All sent requests")

    def add_control_get_recieved_request(self, userID, url):
        self.add_control("bookingmeta:received-requests", method="GET", href=url,
                         title="All received requests")

    def add_control_get_bookables_by(self, userID, url):
        self.add_control("bookingmeta:bookables-by", method="GET", href=url,
                         title="All bookable items which have been created by the user")
