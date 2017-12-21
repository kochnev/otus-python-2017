#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import abc
import pdb
import collections
import datetime
import json
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
    def __init__(self, required, nullable=False):
        self.required = required
        self.nullable = nullable
        self.name = None
        self.value = None

    def __get__(self, obj, objtype):
        return self.value

    def is_valid(self, value):
        return

    def __set__(self, obj, value):
        self.is_valid(value)
        self.value = value

    def __set_name__(self, name):
        self.name = name


class CharField(Field):
    def is_valid(self, value):
        if not isinstance(value, unicode):
            raise ValueError("{0} must be string".format(self.name))

class ArgumentsField(Field):
    def is_valid(self, value):
        if not isinstance(value, collections.Mapping):
            raise ValueError("{0} must be dictionary".format(self.name))


class EmailField(CharField):
    def is_valid(self, value):
        if '@' not in value:
            raise ValueError("{0} must be email address".format(self.name))


class PhoneField(Field):
    def is_valid(self, value):
        s_val = str(value)
        length = len(s_val)
        if not (s_val.isdigit() and length == 11 and s_val.startswith('7')):
            raise ValueError("{0} must be string or numer consisting of 11 \
                             digits and starting with 7")


class DateField(Field):
    def is_valid(self, value):
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("{0} must be date (DD.MM.YYYY)".format(self.name))


class BirthDayField(DateField):
    def is_valid(self, value):
        super(BirthDayField, self).is_valid(value)
        current_year = datetime.datetime.now().year
        value_year = datetime.datetime.strptime(value, '%d.%m.%Y').date().year
        if current_year - value_year > 70:
            raise ValueError("{0} can not be more than 70 years from current \
                             time".format(self.name))


class GenderField(Field):
    def is_valid(self, value):
        if value not in [0, 1, 2]:
            raise ValueError("{0} must be one of the values 0, 1, \
                             2".format(self.name))


class ClientIDsField(Field):
    def is_valid(self, value):
        if not isinstance(value, list):
            raise ValueError("{0} must be array of numbers".format(self.name))


class MetaRequest(type):
    def __new__(meta, name, bases, dct):
        fields = {}
        for attr, obj in dct.items():
            if isinstance(obj, Field):
                fields[attr] = obj
                obj.__set_name__(attr)

        dct['fields'] = fields

        return super(MetaRequest, meta).__new__(meta, name, bases, dct)


class BaseRequest(object):

    __metaclass__ = MetaRequest

    def __init__(self, **kwargs):
        self.errors = []
        self.request = kwargs
        self.is_cleaned = False

    def clean(self):
        for name, f in self.fields.items():
            value = self.request.get(name)
            if not value:
                if f.required:
                    self.errors.append("Field {0} is required".format(name))
                    continue
            if value in ([], {}, '', None):
                if f.nullable:
                    self.errors.append("Field {0} is not nullable".format(name))
                    continue

            try:
                setattr(self, name, value)
            except ValueError as e:
                self.errors.append(str(e))
            
        self.is_cleaned = True


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


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    required_pairs = (
        ('phone', 'email'),
        ('first_name', 'last_name'),
        ('gender', 'birthday')
    )

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)
    
    def get_not_empty_fields(self):
        return  [name for name in self.fields if getattr(self, name) not in ([], {}, '')]


    def is_valid(self):
        super(OnlineScoreRequest, self).is_valid()
        if len(self.errors) > 0:
            return False

        not_empty_fields = self.get_not_empty_fields()
        is_found = False
        for pair in self.required_pairs:
            if set(pair).issubset(not_empty_fields):
                is_found = True
                break

        if not is_found:
            self.errors.append("One of pairs {0} must \
                               exist".format(self.required_pairs))
            return False

        return True 

        

def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + str(ADMIN_SALT)).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = {}, OK

    logging.info("method_handler! "+str(request['body']))
    mr = MethodRequest(**request['body'])
    
    # pdb.set_trace()
    if not mr.is_valid():
        return ' '.join(mr.errors), INVALID_REQUEST
    
    pdb.set_trace()
    if not check_auth(mr):
        return "Forbidden", FORBIDDEN

    # import pdb; pdb.set_trace()
    if mr.method == "online_score":
        osr = OnlineScoreRequest(**mr.arguments)
        if not osr.is_valid():
            return ' '.join(osr.errors), INVALID_REQUEST
        
        ctx['has'] = osr.get_not_empty_fields()
        if request.is_admin:
            score = 42
        else:
            score = scoring.get_score(None, osr.phone, osr.email,
                                      osr.birthday, osr.gender, osr.first_name,
                                      osr.last_name)

        response["score"] = score

    elif mr.method == "clients_interests":
        cir = ClientsInterestsRequest(**mr.arguments)
        if not cir.is_valid():
            return ' '.join(cir.errors), INVALID_REQUEST

        ctx['nclients'] = len(self.client_ids)

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
