from django.urls import path, include

from d11 import views

urlpatterns = [
    path('<int:pk>', include([
        path('.html', views.DocView.as_view(), name='doc-html'),
        path('-aleph-', include([
            path('synopsis.txt', views.DocAlephTxtSynopsisView.as_view()),
            path('dissertation.txt', views.DocAlephTxtDissertationView.as_view()),
        ])),
    ])),
    path('list/', include([
        path('aleph/', include([
            path('create/', include([
                path('all.txt', views.DocAlephTxtBaseListView.as_view(view_mode='create')),
                path('synopsis.txt', views.DocAlephTxtSynopsisListView.as_view(view_mode='create')),
                path('dissertation.txt', views.DocAlephTxtDissertationListView.as_view(view_mode='create')),
            ])),
            path('update/', include([
                path('synopsis.txt', views.DocAlephTxtSynopsisListView.as_view(view_mode='update')),
                path('dissertation.txt', views.DocAlephTxtDissertationListView.as_view(view_mode='update')),
            ])),
        ])),
    ])),
]
