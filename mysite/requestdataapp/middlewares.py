from datetime import datetime
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse


def set_useragent_on_request_middleware(get_response):

    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0
        self.last_time_request = {}
        self.max_requests = 3
        self.limit_time = 10  #seconds

    def __call__(self, request: HttpRequest):
        self.requests_count +=1
        print("request count", self.requests_count)
        response = self.get_response(request)
        self.responses_count +=1
        print("responses count", self.responses_count)
        return response

    def process_exceptions(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")

    def throttling(self,request: HttpRequest):
        user_ip = request.META.get('REMOTE_ADDR')
        curent_datetime = datetime.now()

        if user_ip not in self.last_time_request:
            self.last_time_request[user_ip] = [curent_datetime.timestamp()]
        else:
            if len(self.last_time_request[user_ip]) <= self.max_requests:
                self.last_time_request[user_ip].append(curent_datetime.timestamp())
            elif len(self.last_time_request[user_ip]) > self.max_requests:
                delta = self.last_time_request[user_ip][-1] - self.last_time_request[user_ip][0]
                if delta <= self.limit_time:
                    return HttpResponse("Rate limit exceeded", status=HTTPStatus.TOO_MANY_REQUESTS)
                else:
                    self.last_time_request[user_ip] = [curent_datetime.timestamp()]
