from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from base.consumers import DiagnosisConsumer, IndividualStatisticsConsumer, \
    SimilarDiagnosisConsumer, CustomAnalyticsConsumer
from common.drf.channels_auth_middleware import oAuth2AuthMiddleware

application = ProtocolTypeRouter({

    "websocket": oAuth2AuthMiddleware(URLRouter([
        path("ws/api/diagnosis/", DiagnosisConsumer),
        path("ws/api/individual-statistics/", IndividualStatisticsConsumer),
        path("ws/api/similar-diagnoses/", SimilarDiagnosisConsumer),
        path("ws/api/custom-analytics/", CustomAnalyticsConsumer),
    ])),

})