from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


from ads.models import Ad, Comment, Fav
from ads.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from ads.forms import CreateForm, CommentForm


# NOTICE THAT Each class is a subclass of owner views contained in owner.py file. For more info go to coursera_ads_app/ads/owner.py
# AdList creates a list of the advertisements allocated in the database, and they are shown up in the page 'ad_list'."""
class AdListView(OwnerListView):
    model = Ad
    template_name = "ads/ad_list.html"
    
    """We override the get module of the generic ListView to include the possibility to mark favorite ads. Firstly it checks if a user is authenticated,
    then it retrieves the id field of the favorite ads (line 30) and finally creates a list of the different ids (line 31). 
    For a deeper explanation see: https://www.youtube.com/watch?v=o0XbHvKxw7Y&t=45959s at minute 17:24:45"""
    def get(self, request) :
        ad_list = Ad.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows ]
        
        """Code for the 'search' bar. If the user enters text in it, it will query the database and retrieve all the results which contain
        the searched words either in the title or in the text (line 43-44); if the user hits the search button without writing something,
        the search will show the first 10 ads ordered by the update time."""
        strval =  request.GET.get("search", False)
        if strval :
            """Simple title-only search:
            objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]"""

            # Multi-field search
            # __icontains is for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list adding the updated_at field
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        context = {'ad_list' : ad_list, 'favorites': favorites, 'search': strval}
        return render(request, self.template_name, context)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    
    """We override the get request to include comments in the ad. Here 'retrieved_ad' points to the ad the user chooses to open,
    while 'ad' points to the homonym field in the model 'Comment'; in this way we retrieve a list of comments associated with 
    the chosen ad (comments = Comment.object), ordered by their update time (order_by('-updated_at'))."""
    def get(self, request, pk) :
        retrieved_ad = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=retrieved_ad).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : retrieved_ad, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


class AdDeleteView(OwnerDeleteView):
    model = Ad


# To create an ad we use a form, CreateForm; we override the get method to use this form and create a context dictionary from it.
class AdCreateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    # Pull data
    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        # Diplay some errors if the form is not valid (e.g. title too short)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving. Firstly we save pic with commit=False, so as not to save the form to the database yet.
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    # Works similar to the CreateView, however it first pulls the old data (get_object_or_404 and instance=pic) which will be overwritten.
    def get(self, request, pk):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save
        form.save_m2m()

        return redirect(self.success_url)

    
def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response


# Pull ad data from the database, post a comment, then redirect the user to the ad detail page
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        ad = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=ad)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/ad_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])


# csrf_exempt tells the view not to create a csrf token
@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
