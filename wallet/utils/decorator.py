import json
import requests
from django.shortcuts import render, redirect


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
            redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard/"
            return redirect(redirect_url)
        else:
            try:
                print("----get-session",session_id)
                
                url = "https://100014.pythonanywhere.com/api/userinfo/"
                body = {"session_id": session_id}
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, data=json.dumps(body), headers=headers).json()
                print("res",res)
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
                redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://localhost:3000/100088-dowellwallet/"
                # redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard/"
                return redirect(redirect_url)

    return wrapper
