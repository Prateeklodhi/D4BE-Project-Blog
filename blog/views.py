from django.core.mail import send_mail
from django.db.models import Count 
from django.shortcuts import render,get_object_or_404
from django.http import Http404
from taggit.models import Tag
from .models import Post,Comment
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator,EmptyPage ,PageNotAnInteger# Paginator is used for pagination
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm, SearchForm
from django.views.decorators.http import require_POST
# Create your views here.
'''class PostListView(ListView):
    #for better understading lookthrough the django4byexample page number 59
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name ='blog/post/list.html'''

def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag,slug= tag_slug)
        post_list = post_list.filter(tags__in = [tag])
    # Let's Create pagination for 3 post per page
    paginator = Paginator(post_list,3)# post_list = function name which a view here and 3 is number of posts(objects) that will be gonna display on per page
    page_number = request.GET.get('page',1)
    print(page_number)# this parameter contains the requested page number if page parameter is not in the GET parameters of the request we use the defalut value 1 to load the first page of result.
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
        print(posts)#we obtain the objects for the desired page by calling the page() method of the Paginator. This method returns a page object that we store in the posts variable. We pass the Page number as parameter. 
    return render(request,'blog/post/list.html',{'posts':posts,'tag':tag})


def post_search(request):
    form = SearchForm()
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # search_vector = SearchVector('title',weight='A',)+SearchVector('body',weight='B')
            # search_query = SearchQuery(query)
            # result = Post.published.annotate(search=search_vector,rank=SearchRank(search_vector,search_query)).filter(rank__gte=0.3).order_by('-rank')#for reference goto page number 141 Steamming
            result = Post.published.annotate(similarity=TrigramSimilarity('title',query)).filter(similarity__gt=0.1).order_by('-similarity')#for reference goto page number 141 Steamming
    return render (request,'blog/post/search.html',{'form':form,'query':query,'result':result})

def post_detail(request,year,month,day,post):
    '''try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No page found.') 
    # Another way to the same using get object or 404'''
    
    post = get_object_or_404(Post,
            publish__year = year,
            publish__month = month,
            publish__day = day,
            slug = post
            , status = Post.Status.PUBLISHED)
    #List of active comment for this post
    comments = post.comments.filter(active = True)# in model related name = comments
    # form for users to comment
    form = CommentForm()
    #list of similar posts for reference go to page number 102.
    post_tags_ids = post.tags.values_list('id',flat =True)
    similar_posts = Post.published.filter(tags__in = post_tags_ids)\
        .exclude(id =post.id)
    similar_posts = similar_posts.annotate(same_tags = Count('tags'))\
        .order_by('-same_tags','-publish')[:4]
    return render(request,'blog/post/detail.html',{'post':post,'comments':comments,'form':form,'similar_posts':similar_posts})


def post_share(request,post_id):
    post = get_object_or_404(Post,id = post_id,status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject  = f"{cd['name']}recommends you read"\
                f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject,message,'prateeklodhigloitel@gmail.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent})


@require_POST
def post_comment(request,post_id):
    post = get_object_or_404(Post,id=post_id,status = Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        #save the comment to the database
        comment.post = post
        comment.save()
    return render(request,'blog/post/comment.html',{'post':post,'form':form,'comment':comment})
