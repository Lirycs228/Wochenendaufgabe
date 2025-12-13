from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import AskForm
import requests

# Create your views here.
def index(request):
    template = loader.get_template("chat/index.html")
    return HttpResponse(template.render({}, request))


def get_ask(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = AskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print
            response = requests.post(
                "http://127.0.0.1:5678/webhook/fd2f6a34-2a8f-4580-b53f-d24102e01d4f",
                data={
                    "query": form.cleaned_data.get("ask"),
                    "sessionId": "sdfghj"
                    }
                )
            
            if response.status_code == 200:
                print("Success!")
            elif response.status_code == 404:
                print("Not Found.")

            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/thanks/")
    else:
        form = AskForm()

    return render(request, "chat/ask.html", {"form": form})