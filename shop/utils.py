from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_queryset(request, queryset, per_page=10, page_param='page'):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get(page_param, 1)
    
    try:
        paginated_page = paginator.page(page)
    except PageNotAnInteger:
        paginated_page = paginator.page(1)
    except EmptyPage:
        paginated_page = paginator.page(paginator.num_pages)
    
    return paginated_page
