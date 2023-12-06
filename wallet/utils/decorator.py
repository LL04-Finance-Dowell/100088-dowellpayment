import json
import requests
from django.shortcuts import render, redirect
import jwt
from django.http import HttpResponseBadRequest
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


def user_is_authenticated(view_func):
    """
    Decorator to check if the user is authenticated.
    Redirects to a login page if the user is not authenticated.
    """

    def wrapper(request, *args, **kwargs):
        print("entering wrapper function")
        
        session_id = request.GET.get("session_id", None)
        print(session_id)

        if session_id is None:
            print("session is none")
            redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/"
            return redirect(redirect_url)
        else:
            try:
                print("----get-session",session_id)
                
                url = "https://100014.pythonanywhere.com/api/userinfo/"
                body = {"session_id": session_id}
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, data=json.dumps(body), headers=headers).json()
                # print("res",res)
                username = res["userinfo"]["username"]
                email = res["userinfo"]["email"]
                firstname = res["userinfo"]["first_name"]
                lastname = res["userinfo"]["last_name"]
                phone = res["userinfo"]["phone"]
                profile_picture = res["userinfo"]["profile_img"]

                # Call the original view function with the username and email
                

                return view_func(
                    request,
                    username=username,
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    phone=phone,
                    profile_picture=profile_picture,
                    sessionID=session_id,
                    *args,
                    **kwargs
                )
            except Exception as e:
                print('error',e)
                redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/"
                # redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard/"
                return redirect(redirect_url)

    return wrapper




def jwt_decode(view_func):
    """
    Decorator to check if the user is authenticated.
    Redirects to a login page if the user is not authenticated.
    """

    def wrapper(request, *args, **kwargs):
        print("entering session id and jwt wrapper function")
        
        session_id = request.GET.get("session_id", None)
        print(session_id)

        if session_id is None:
            print("session is none")
            redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/login/"
            return redirect(redirect_url)
        else:
            try:


                print("----get-session",session_id)
                
                url = "https://100014.pythonanywhere.com/api/userinfo/"
                body = {"session_id": session_id}
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, data=json.dumps(body), headers=headers).json()
                # print("res",res)
                username = res["userinfo"]["username"]
                email = res["userinfo"]["email"]
                firstname = res["userinfo"]["first_name"]
                lastname = res["userinfo"]["last_name"]
                phone = res["userinfo"]["phone"]
                profile_picture = res["userinfo"]["profile_img"]



                try:
                    _, token = request.headers.get('Authorization').split()
                    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    print("decoded_payload",decoded_payload)
                    id = decoded_payload.get('id')
                    jwt_username = decoded_payload.get('username')
    
                    if username != jwt_username:
                        print("--------------it is not equal--------------")
                        return HttpResponseBadRequest("Unauthorized")
                    
                    # Add any other necessary attributes based on the structure of your payload

                except jwt.ExpiredSignatureError:
                    return HttpResponseBadRequest("Token has expired")
                except jwt.InvalidTokenError as e:
                    print("Invalid Token Error:", e)
                    return HttpResponseBadRequest("Invalid token")

                # Call the original view function with the username and email
            
                return view_func(
                    request,
                    username=username,
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    phone=phone,
                    profile_picture=profile_picture,
                    sessionID=session_id,
                    *args,
                    **kwargs
                )
            except Exception as e:
                print('error',e)
                # redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/"
                redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/login/"
                return redirect(redirect_url)

    return wrapper


