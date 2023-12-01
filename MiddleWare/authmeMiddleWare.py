import os
from typing import Any
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import jwt
import logging

from Users.models import Users

logger = logging.getLogger(__name__)

class AuthMe:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        try:
            print("Auth me")
            Allowed_paths = ["/users/log-in" , "/users/sign-up" , "/admin/"]
            response = self.get_response(request)
            token = request.get_signed_cookie('authorization', salt=os.environ.get('SECRET_KEY'), default=None)

            if request.path in Allowed_paths:
                return response

            if token is None:
                return HttpResponseRedirect("/users/log-in")

            token = token.split(" ")[1]
            decodedData = jwt.decode(
                token,
                os.environ.get('SECRET_KEY'),
                algorithms=['HS256']
            )

            user = Users.objects.filter(_id = decodedData['_id'])

            if(len(user) == 0):
                return HttpResponseRedirect("/users/log-in")
            
            user = list(user.values())[0]

            request.session['user'] = {
                '_id' : user['_id'],
                'firstName' : user['firstName'],
                'middlename' : user['middleName'],
                'lastName' : user['lastName'],
                'DOB' : user['DOB'],
                'email' : user['email'],
                'phoneNumber' : user['phoneNumber'],
                'slug' : user['slug'],
                'address_id' : user['address_id'],
            }
            return response

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return HttpResponseRedirect("/users/log-in")

        except jwt.InvalidSignatureError:
            logger.warning("Invalid signature")
            return HttpResponseRedirect("/users/log-in")

        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return HttpResponseRedirect("/users/log-in")

        except Exception as e:
            logger.exception("Error in AuthMe middleware")
            return HttpResponseRedirect("/users/log-in")
