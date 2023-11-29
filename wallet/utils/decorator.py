import json
import requests
from django.shortcuts import render, redirect


def user_is_authenticated(view_func):
    """
    Decorator to check if the user is authenticated.
    Redirects to a login page if the user is not authenticated.
    """

    def wrapper(request, *args, **kwargs):
        try:
            user_session = request.session["session_id"]
            print("usersession", user_session)
            url = "https://100014.pythonanywhere.com/api/userinfo/"
            body = {"session_id": user_session}
            headers = {"Content-Type": "application/json"}
            try:
                res = requests.post(url, data=json.dumps(body), headers=headers).json()
                # print("-------------res------------", res)
                username = res["userinfo"]["username"]
                email = res["userinfo"]["email"]
                firstname = res["userinfo"]["first_name"]
                lastname = res["userinfo"]["last_name"]
                phone = res["userinfo"]["phone"]
                profile_picture = res["userinfo"]["profile_img"]
                sessionID = user_session
                print("----running------")
                # Call the original view function with the username and email
                return view_func(
                    request,
                    username=username,
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    phone=phone,
                    profile_picture=profile_picture,
                    sessionID=sessionID,
                    *args,
                    **kwargs
                )
            except:
                request.session.clear()
                print("----session deleted--------")
                redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard"
                return redirect(redirect_url)

        except:
            print("---------re-running---------")
            # Check if request has GET attribute
            if not hasattr(request, "GET"):
                return redirect(
                    "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard"
                )

            # Try to get session_id from GET parameters
            session_id = request.GET.get("session_id", None)

            if session_id is None:
                redirect_url = "https://100014.pythonanywhere.com?redirect_url=http://127.0.0.1:8000/api/wallet/v1/wallet-dashboard"
                return redirect(redirect_url)
            else:
                request.session["session_id"] = session_id
                url = "https://100014.pythonanywhere.com/api/userinfo/"
                body = {"session_id": session_id}
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, data=json.dumps(body), headers=headers).json()

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

    return wrapper
