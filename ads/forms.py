from django import forms
from ads.models import Ad
from django.core.files.uploadedfile import InMemoryUploadedFile
from ads.humanize import naturalsize


"""Forms are necessary when it comes to retrieve data from the user, as they allow users to post stuff
in our website. Here we have a form that handles the creation and the update of the ads by the users."""
class CreateForm(forms.ModelForm):
    """max_upload_limit and max_upload_limit_text check for the size of the uploaded image, which cannot be larger than 
    the value in max_upload_limit, which corresponds to 2 megabytes (the calculation is handled in humanize.py file)."""
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)
    
    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = Ad
        fields = ['title', 'text', 'price', 'picture', 'tags']

    # Check if the size of the picture is less than the one specified (see above).
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")

    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(CreateForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            self.save_m2m()

        return instance

# Handle the users' comments
class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
