from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.list import ListView

from django.contrib.auth.mixins import LoginRequiredMixin


"""Here we subclass the generic List, Detail, Create, Update and Delete views so as to add an owner to some of them. Actually, the views in which the user field is 
added are Create, Update and Delete."""
class OwnerListView(ListView):
    """
    Sub-class the ListView to pass the request to the form.
    """


class OwnerDetailView(DetailView):
    """
    Sub-class the DetailView to pass the request to the form.
    """


class OwnerCreateView(LoginRequiredMixin, CreateView):
    """
    Sub-class of the CreateView to automatically pass the Request to the Form
    and add the owner to the saved object.
    """

    """We override the form_valid method to check if the owner corresponds to the login user. The object is firstly saved with 'commit=save' so that it is not
    stored in the database yet. 
    Form_valid at the end redirects automatically to get_success_url: https://docs.djangoproject.com/en/3.0/ref/class-based-views/mixins-editing/#django.views.generic.edit.ModelFormMixin.form_valid
    This method is taken from: https://stackoverflow.com/a/15540149 """
    def form_valid(self, form):
        print('form_valid called')
        object = form.save(commit=False)
        object.owner = self.request.user
        object.save()
        return super(OwnerCreateView, self).form_valid(form)


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    """
    Sub-class the UpdateView to pass the request to the form and limit the
    queryset to the requesting user.
    """
    
    """The user check is made when a user pull a queryset. Queryset is a collection of objects (or queries) from the database; 
    adding the filter 'owner=self.request.user' we limit the queryset to only the owned objects. The process is the same for the Delete view below."""
    def get_queryset(self):
        print('update get_queryset called')
        """ Limit a User to only modifying their own data. """
        qs = super(OwnerUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    """Sub-class the DeleteView to restrict a User from deleting other
    user's data.
    Other ways to modify the view: https://stackoverflow.com/questions/5531258/example-of-django-class-based-deleteview """

    def get_queryset(self):
        print('delete get_queryset called')
        qs = super(OwnerDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)
