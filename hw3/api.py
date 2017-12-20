#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
import scoring
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable
        self.value = None

    def __get__(self, obj, objtype):
        return self.value

    def __set__(self, obj, value):
        self.value = value


class CharField(Field):
    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError("Must be a string")
        if not self.nullable and not value:
            raise ValueError("The field is not nullable")
        self.value = value




class ArgumentsField(Field):
    pass


class EmailField(CharField):
    pass


class PhoneField(Field):
    pass


class DateField(Field):
    pass


class BirthDayField(Field):
    pass


class GenderField(Field):
    pass


class ClientIDsField(Field):
    pass

class MetaRequest(type):
    def __new__(meta, name, bases, dct):
        fields = {}
        for k, v in dct.items():
            if isinstance(v, Field):
                fields[k] = v

        dct['fields'] = fields
        
        return super(MetaRequest, meta).__new__(meta, name, bases, dct)


class BaseRequest(object):

    __metaclass__ = MetaRequest

    def __init__(self, **kwargs):
        self.errors = []
        self.request = kwargs
        self.is_cleaned = False

        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def clean(self):
        for name, f in self.fields.items():
            if f.required and not self.request.get(name, False):
                self.errors.append("Field {} is required".format(name))
                continue


        self.is_cleaned = True
        return

    def is_valid(self):
        if not self.is_cleaned:
            self.clean()
        return not self.errors


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") /
                                + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account /
                                + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    # response, code = None, None
    # return response, code
    response, code = {}, OK

    logging.info("method_handler! "+str(request['body']))
    import pdb; pdb.set_trace()
    mr = MethodRequest(**request['body'])
    # import pdb; pdb.set_trace()
    if mr.method == "online_score":
        osr = OnlineScoreRequest(**mr.arguments)
        score = scoring.get_score(store=None, **mr.arguments)
        response["score"] = score
    elif mr.method == "clients_interests":
        cir = ClientsInterestsRequest(**mr.arguments)
        for cid in cir.client_ids:
            interests = scoring.get_interests(None, cid)
            response[cid] = interests
    else:
        code = BAD_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            logging.info("data_string! "+data_string)
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST
        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" %
                         (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({
                                                        "body": request,
                                                        "headers": self.headers
                                                       },
                                                       context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"),
                 "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
