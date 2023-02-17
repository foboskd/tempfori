from functools import partial
from drf_yasg import openapi

openapi_response_user = partial(openapi.Response, 'If the user is logged in')
openapi_response_guest = partial(openapi.Response, "If the user isn't logged in")

openapi_manual_parameter_bool = partial(
    openapi.Parameter,
    type=openapi.TYPE_BOOLEAN,
    required=False
)
openapi_manual_parameter_array = partial(
    openapi.Parameter,
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_INTEGER),
    required=False
)
