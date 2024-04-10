from django.urls import path
from .views import AddRemark, Allcases, CaseDetails, Daily_Activity, SearchCase, TableData, Weekly_Activity

# get all people posted missing and found in a day and do a summary location sexget all people then generate reports
# at 12 on daily basis
# do the same in monthly and yearly
# where do many people go missing
# what sex has many people missing
"""
Daily Activity Report:
Weekly/Monthly Activity Summary:
Case Status Report:
Face Recognition Performance Report:
Geographical Distribution Report:
User Activity Report:
"""
urlpatterns = [
    path('reports/daily/<int:y>/<int:m>/<int:d>/',
         Daily_Activity.as_view(), name='daily_activity'),
    path('reports/weekly/<int:y>/<int:m>/<int:d>/',
         Weekly_Activity.as_view(), name='weekly_report'),
    path('reports/cases/', Allcases.as_view(), name='get all cases'),
    path('reports/cases/<str:id>/', CaseDetails.as_view(), name='get single case'),
    path('notify/case/status/<int:id>/',
         AddRemark.as_view(), name='add remark and notify'),
    path('data/table/',
         TableData.as_view(), name='get dates of mps and fps'),
    path('search/case/',
         SearchCase.as_view(), name='search a single case')
]
