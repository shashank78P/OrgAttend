import os
from typing import Any
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
import jwt
from django.utils import timezone

from Users.models import Users , Address

class AuthMe:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        try:
            Allowed_paths = ["/users/log-in" , "/users/sign-up" , "/admin/" , "/users/sign-up-2","/users/change-password-pre","/users/change-password"]
            response = self.get_response(request)
            token = request.get_signed_cookie('authorization', salt=os.environ.get('SECRET_KEY'), default=None)

            print("request.path")
            print(request.path)

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
            address = Address.objects.get(id = user["address_id"])

            request.session['user'] = {
                '_id' : user['_id'],
                'firstName' : user['firstName'],
                'middleName' : user['middleName'],
                'lastName' : user['lastName'],
                'DOB' : user['DOB'].strftime('%Y-%m-%d'),
                'currentActiveOrganization' : user['currentActiveOrganization'],
                'email' : user['email'],
                'phoneNumber' : user['phoneNumber'],
                'slug' : user['slug'],
                'address_id' : user['address_id'],
                'city' : address.city,
                'state' : address.state,
                'country' : address.country,
                'code' : address.code,
            }
            print("exiting from middle ware")
            return response

        except jwt.ExpiredSignatureError:
            return HttpResponseRedirect("/users/log-in")

        except jwt.InvalidSignatureError:
            return HttpResponseRedirect("/users/log-in")

        except jwt.InvalidTokenError:
            return HttpResponseRedirect("/users/log-in")

        except Exception as e:
            return HttpResponseRedirect("/users/log-in")
