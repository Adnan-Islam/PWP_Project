import json
from flask import Response

# Global Variables
MASON = "application/vnd.mason+json"
LINK_RELATIONS_URL = "https://bookingmanagementsystem1.docs.apiary.io/#reference/link-relations"
PRODUCT_PROFILE = "/profiles/product/"
ERROR_PROFILE = "/profiles/error/"

#This class is taken from the course material of PWP in University of Oulu, in this link
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2020/implementing-rest-apis-with-flask/
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
    """
    Utils class for keeping utility functions in a place. All functions are static.
    """
    
    @staticmethod
    def create_error_response(status_code=None, title=None, message=None, path=None):
        """
        Creates an error response using for mason type using the given parameters.

        : param str status_code: the status code of the response
        : param str title: the title of the error
        : param str message: the message of the error
        : param str tipathtle: the path that the error occured
        : output Response: created response using the information provided in parameters
        """
        resource_url = path
        body = MasonBuilder(resource_url=resource_url)
        body.add_error(title, message)
        body.add_control("profile", href=ERROR_PROFILE)
        return Response(json.dumps(body), status_code, mimetype=MASON)



class UserItemBuilder(MasonBuilder):
    """
    A extended class of MasonBuilder. Specified to add some specific controls that belong to UserItem resources
    """
    
    @staticmethod
    def user_schema():
        """
        A static method to get the user object's schema
        
        :output dict schema: dictionary type object schema
        """
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

    def add_control_edit_user(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the edit control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("edit", method="PUT", href=url,
                         encoding="json", schema=self.user_schema())

    def add_control_delete_user(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the deleete control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("delete", method="DELETE", href=url,
                         encoding="json")

    def add_control_add_user(self, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the edit control.
        
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:add-user", method="POST", href=url,
                         encoding="json", schema=self.user_schema())

    def add_control_get_all_bookables(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the all-bookables control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """        self.add_control("bookingmeta:all-bookables", method="GET", href=url,
                         title="Bookables collection of a User")

    def add_control_get_sent_request(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the sent-requests control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:sent-requests", method="GET", href=url,
                         title="All sent requests")

    def add_control_get_recieved_request(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the received-requests control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:received-requests", method="GET", href=url,
                         title="All received requests")

    def add_control_get_bookables_by(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the bookables-by control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:bookables-by", method="GET", href=url,
                         title="All bookable items which have been created by the user")


class BookableBuilder(MasonBuilder):
    """
    A extended class of MasonBuilder. Specified to add some specific controls that belong to Bookable resources
    """ 
    
    @staticmethod
    def bookable_schema():
        """
        A static method to get the Bookable object's schema
        
        :output dict schema: dictionary type object schema
        """
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "bookalbe's name",
            "type": "string"
        }
        props["detail"] = {
            "description": "bookable detail",
            "type": "string"
        }
        return schema

    def add_control_user(self, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the user control.
        
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:user",  href=url, title = "User Item")

    def add_control_add_bookable(self, user_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the add control.
        
        : param str user_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:add", method="POST", href=url, 
                         title="Add Bookable to the users bookables list", schema=self.bookable_schema())

    def add_control_slots_of(self, user_id, bookable_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the slots-of control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:slots-of", href=url,
                         title="Slots collection of this Bookable owned by the User")

    def add_control_edit(self, user_id, bookable_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the edit control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("edit", method="PUT", href=url,
                         encoding="json", title="Edit Bookable", schema=self.bookable_schema())

    def add_control_delete(self, user_id, bookable_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the delete control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("delete", method="Delete", href=url,
                         title="Delete the bookable")


class SlotBuilder(MasonBuilder):
    """
    A extended class of MasonBuilder. Specified to add some specific controls that belong to Bookable resources
    """ 
    
    @staticmethod
    def slot_schema():
        """
        A static method to get the Slot object's schema
        
        :output dict schema: dictionary type object schema
        """
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["availability"] = {
            "description": "Availability of the slot",
            "type": "boolean"
        }
        props["starting_time"] = {
            "description": "Starting time as datetime",
            "type": "datetime"
        }
        props["ending_time"] = {
            "description": "Ending time as datetime",
            "type": "datetime"
        }
        return schema

    def add_control_user(self, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the user control.
        
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:user",  href=url, title = "User Item")

    def add_control_add_slot(self, user_id, bookable_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the add control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:add", method="POST", href=url,
                         title="Add Slot to the users slots list", schema=self.slot_schema())

    def add_control_bookable(self, user_id, bookable_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the bookable control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("bookingmeta:bookable", href=url,
                         title="Bookable item that the Slot belongs to")

    def add_control_edit(self, user_id, bookable_id, slot_id, url):
        """
        A specified extension of function add_control in MasonBuilder. 
        Used to add the edit control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str slot_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("edit", method="PUT", href=url,
                         encoding="json", title="Edit Slot", schema=self.slot_schema())

    def add_control_delete(self, user_id, bookable_id, slot_id, url):
        """
        A specified delete of function add_control in MasonBuilder. 
        Used to add the bookable control.
        
        : param str user_id: used in the url
        : param str bookable_id: used in the url
        : param str slot_id: used in the url
        : param str url: the url that this control leads to
        """
        self.add_control("delete", method="Delete", href=url,
                         title="Delete the Slot")
