from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

from taggit.managers import TaggableManager


"""This is the main class of the app, Ad has the fundamental fields to create an advertisement. The fields are created thanks to built-in classes
such as TextField for a text, DecimalField for decimal numbers, BinaryField for binary files like music tracks or images. More info at:
https://www.geeksforgeeks.org/django-model-data-types-and-fields-list/
We also use ManyToManyField, for comments and favorites, because comments can be written by different users, so as a user can type multiple comments.
For more info on ManyToMany: 
    - https://www.sankalpjonna.com/learn-django/the-right-way-to-use-a-manytomanyfield-in-django
    - https://www.geeksforgeeks.org/related_name-django-built-in-field-validation/
Finally, content-type specifies the type of the image, if uploaded.For more info about MIMEtype: 
https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_type """
class Ad(models.Model) :
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    text = models.TextField()
    """We use AUTH_USER_MODEL (which has a default value if it is not specified in settings.py) to create a Foreign Key relationship between the Ad model 
    and a django built-in User model"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment', related_name='comments_owned')
    picture = models.BinaryField(null=True, editable=True)
    tags = TaggableManager(blank=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Fav', related_name='favorite_ads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list ordered by the title
    def __str__(self):
        return self.title

    
"""Take care of the comments section. Other than the text field, there is a relation with the Ad class:
for each Ad there are different comments wrote by different users."""
class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    """Shows up in the admin list by name. There are two possibilities handled by an if statement:
    1. If the text length is less than 15 characters, the comment is entirely shown up in the page.
    2. Otherwise, if it is greater than 15 characters, it will print the first 11 characters plus three dots
    at the end (they mark that there is other written text."""
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

    
"""This handles the favourite button. It is simply linked to the ad, which can be
chosen as favourite by different users, as well as an user can choose several ads as
favourites."""
class Fav(models.Model) :
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    """unique_together is a metadata option which allows to consider different fields as unique.
    For an entry, it is considered different from others if at least of the fields specified in the option
    is different. Here it constrains users to select an ad as favourite only one time. This can be quite
    tricky to understand, I suggest looking at the links below for a deeper explanation:
    - https://docs.djangoproject.com/en/3.2/ref/models/options/#unique-together
    - An expanded explanation of the docs: https://blog.katastros.com/a?ID=01300-36d18c12-5fa5-433a-960d-6ee0183b8b53
    - An explanation which adds a different perspective: 
      http://www.learningaboutelectronics.com/Articles/How-to-make-fields-of-a-database-table-unique-together-in-Django.php """
    class Meta:
        unique_together = ('ad', 'user')
        
    """What we have seen before but with some string formatting. Basically the '%' sign indicates
    the beginning of the specifier, while the 's' converts everything into a string 
    (it calls the str() class). More info at:
    - https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
    - https://realpython.com/python-string-formatting/#1-old-style-string-formatting-operator"""
    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.ad.title[:10])
