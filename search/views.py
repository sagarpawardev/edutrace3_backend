from rest_framework import generics, permissions, status, filters

# Create your views here.


from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings

from django.db.models import Max, Q

from search.models import CollegeResult
from search.permissions import ReadOnly
from search.serializers import CollegeResultSerializer


class CollegeSearchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = CollegeResult.objects.all()
    serializer_class = CollegeResultSerializer
    permission_classes = (ReadOnly,)  # (permissions.IsAuthenticatedOrReadOnly, ReadOnly,)


class CitySearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed.
    """
    queryset = CollegeResult.objects.all()
    serializer_class = CollegeResultSerializer
    # permission_classes = (ReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('cutoff_type')


class BranchSearchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CollegeResult.objects.all()
    serializer_class = CollegeResultSerializer
    permission_classes = (ReadOnly,)


class AdvanceSearchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CollegeResult.objects.all()
    serializer_class = CollegeResultSerializer
    permission_classes = (ReadOnly,)


@api_view(["GET"])
def college_search(request):
    if request.method == 'GET':

        # Handle Request Params
        college_id = request.query_params.get('id', None)

        # Query DB
        queryset = CollegeResult.objects.all()
        if college_id is not None:
            queryset = queryset.filter(college_code=college_id)

        # Apply Pagination
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CollegeResultSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def branch_search(request):
    if request.method == 'GET':

        # Handle Request Params
        name = request.query_params.get('name', None)
        code = request.query_params.get('code', None)

        # Query DB
        queryset = CollegeResult.objects.all()
        if name is not None:
            queryset = queryset.filter(branch_name__icontains=name)
        if code is not None:
            queryset = queryset.filter(branch_code__icontains=id)

        # Apply Pagination
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CollegeResultSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def city_search(request):
    if request.method == 'GET':

        # Handle Request Params
        name = request.query_params.get('name', None)

        # Query DB
        queryset = CollegeResult.objects.all()
        if name is not None:
            queryset = queryset.filter(city__icontains=name)

        # Apply Pagination
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CollegeResultSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def advance_search(request):
    if request.method == 'GET':
        # Handle Request Params
        mark = request.query_params.get('mark', None)
        city = request.query_params.get('city', None)
        branch_name = request.query_params.get('branch', None)
        college_name = request.query_params.get('college', None)

        # Query DB
        # queryset = CollegeResult.objects.all()
        eligible_quotas = tuple(['AI'])  # TODO Fix This
        eligible_quotas_str = str(','.join(["%s"] * len(eligible_quotas)))
        query = 'SELECT a.college_code college_code, ' + \
                'a.branch_name branch_name, ' + \
                'a.college_name college_name, ' + \
                'max_cutoff_rank stage_rank, ' + \
                'cutoff_type cutoff_type, ' + \
                'a.stage_mark stage_mark, ' + \
                'a.id id ' + \
                'FROM   vw_college_result a, ' + \
                '   (SELECT college_code, ' + \
                '           branch_name, ' + \
                '           Min(stage_rank) max_cutoff_rank ' + \
                '       FROM  ( ' + \
                '			    SELECT college_code, ' + \
                '                   branch_name, ' + \
                '                   stage_rank ' + \
                '			    FROM   vw_college_result ' + \
                '			    WHERE  cutoff_type IN (%s) ' + \
                '		    ) ' + \
                '        GROUP BY college_code, branch_name' \
                '       ) b ' + \
                'WHERE  a.college_code = b.college_code ' + \
                '   AND a.branch_name = b.branch_name ' + \
                '   AND a.stage_rank = max_cutoff_rank ' + \
                '   AND cutoff_type IN (%s) ' + \
                'ORDER  BY a.stage_mark DESC '
        query = query % (eligible_quotas_str, eligible_quotas_str)
    # print(query)

    # query = "SELECT * from vw_college_result where cutoff_type IN (%s) " % eligible_quotas_str
    # queryset = CollegeResult.objects.raw(query, params=eligible_quotas)
    eligible_quotas = eligible_quotas + eligible_quotas

    queryset = CollegeResult.objects.raw(query, params=eligible_quotas)


    '''
    quota =
    query1 = CollegeResult.objects.filter(cutoff_type__in=quota)
    query2 = query1.values('college_code', 'branch_name').annotate(stage_mark=Max('stage_mark'))
    
    query3 = query1.filter()
    q_statement = Q()
    for college in query2:
        q_statement |= (Q(college_code=college['college_code']) & Q(branch_name=college['branch_name']) & Q(
            stage_mark=college['stage_mark']))

    query3 = query1.filter(q_statement)

    query3.filter()
    print("SGR", query3)
    '''

    # queryset = CollegeResult.objects.raw(' SELECT * from vw_college_result')

    queryset = list(queryset)

    if mark is not None:
        queryset = queryset.filter(stage_mark__lte=mark)
    if city is not None:
        queryset = queryset.filter(city__icontains=city)
    if branch_name is not None:
        queryset = queryset.filter(branch_name__icontains=branch_name)
    if college_name is not None:
        queryset = queryset.filter(college_name__icontains=college_name)

    # Apply Pagination
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request)
    serializer = CollegeResultSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)
