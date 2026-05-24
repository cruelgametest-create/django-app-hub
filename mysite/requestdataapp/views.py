from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UserBioForm, UploadFileForm

def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # myfile = request.FILES["myfile"]
            myfile = form.cleaned_data["file"]
            fs = FileSystemStorage()
            max_size = 1048576
            if myfile.size < max_size:
                filename = fs.save(myfile.name, myfile)
                print(f"saved file: {filename}, size: {myfile.size} bytes")
            else:
                print(f"The max size for a file is {max_size} bytes")
    else:
        form = UploadFileForm()
    context = {
        "max_size": 1,
        "form": form,
    }
    return render(request, "requestdataapp/file-upload.html", context=context)
