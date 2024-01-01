import os
from typing import Any
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
import jwt
from django.utils import timezone

import logging
from Organization.models import Employee, OwnerDetails
logger = logging.getLogger(__name__)

from Users.models import Users , Address

class AuthMe:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) :
        try:
            print("Middle ware called")
            Allowed_paths = ["/users/log-in" , "/users/sign-up" , "/admin/" , "/users/sign-up-2","/users/change-password-pre","/users/change-password"]
            print("Middle ware cheking for token")
            token = request.get_signed_cookie('authorization', salt=os.environ.get('SECRET_KEY'), default=None)

            print("request.path")
            print(request.path)
            print(token)
            logger.info(f"Checking token for path: {request.path}")

            if request.path in Allowed_paths:
                logger.warning("Redirecting to users-log-in due to missing token")
                response = self.get_response(request)
                return response

            if token is None:
                logger.info("Redirecting to user profile page")
                return HttpResponseRedirect(reverse("users-log-in"))
            else:
                token = token.split(" ")[1]
                decodedData = jwt.decode(
                    token,
                    os.environ.get('SECRET_KEY'),
                    algorithms=['HS256']
                )
                print(token)
                print(decodedData)

                userData = Users.objects.filter(_id = decodedData['_id'])
                print(userData)
                print(len(userData))

                if(len(userData) == 0):
                    return HttpResponseRedirect(reverse("users-log-in"))

                user = list(userData.values())[0]
                print(user)
                # address= {
                #     'address_id' : -1,
                #     'city' : "",
                #     'state' : "",
                #     'country' : "",
                #     'code' : "",
                #     }
                # if(user["address_id"] is not None):
                #     address = Address.objects.filter(id = user["address_id"])
                #     if len(address) > 0:
                #         address = address[0]
                #         print(address)

                currentActiveOrganization = -1
                print("currentActiveOrganization")
                print(currentActiveOrganization)
                print(userData)
                print(user['currentActiveOrganization'])
                if(user['currentActiveOrganization'] == -1):
                    print("currentActiveOrganization is -1")
                    userInOrg = Employee.objects.filter(employee = userData[0]).first()
                    print(userInOrg)
                    userInOrgOwner = OwnerDetails.objects.filter(userId = userData[0]).first()
                    print(userInOrgOwner)

                    if(userInOrg is not None):
                        currentActiveOrganization = userInOrg.Organization._id
                        Users.objects.filter(_id = decodedData['_id']).update(currentActiveOrganization = userInOrg.Organization._id)
                    if(userInOrgOwner is not None):
                        currentActiveOrganization = userInOrgOwner.OrganizationId._id
                        Users.objects.filter(_id = decodedData['_id']).update(currentActiveOrganization = userInOrg.Organization._id)


                request.session['user'] = {
                    '_id' : user['_id'],
                    'firstName' : user['firstName'],
                    'middleName' : user['middleName'],
                    'lastName' : user['lastName'],
                    'DOB' : user['DOB'].strftime('%Y-%m-%d') if user['DOB'] is not None else "",
                    'currentActiveOrganization' : user['currentActiveOrganization'] if user['currentActiveOrganization'] != -1 else currentActiveOrganization,
                    'email' : user['email'],
                    'phoneNumber' : user['phoneNumber'],
                    'slug' : user['slug'],
                    'address_id' : user['address_id'],
                    # 'city' : address["city"],
                    # 'state' : address["state"],
                    # 'country' : address["country"],
                    # 'code' : address["code"],
                }
                print("exiting from middle ware")

                if(request.path == "/"):
                    logger.info("Redirecting to user profile page")
                    return HttpResponseRedirect(f"/users/{user['slug']}")
                logger.info("Exiting from middleware")

            response = self.get_response(request)
            return response

        except jwt.ExpiredSignatureError:
            logger.error("Redirecting to users-log-in due to ExpiredSignatureError")
            return HttpResponseRedirect(reverse("users-log-in"))

        except jwt.InvalidSignatureError:
            logger.error("Redirecting to users-log-in due to InvalidSignatureError")
            return HttpResponseRedirect(reverse("users-log-in"))

        except jwt.InvalidTokenError:
            logger.error("Redirecting to users-log-in due to InvalidTokenError")
            return HttpResponseRedirect(reverse("users-log-in"))

        except Exception as e:
            print("====================================================")
            print(e)
            logger.exception("An unexpected error occurred")
            return HttpResponseRedirect(reverse("users-log-in"))
