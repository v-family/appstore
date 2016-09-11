from django.forms import Form, CharField, Textarea, ChoiceField, RadioSelect, \
    BooleanField, TextInput
from django.utils.translation import ugettext_lazy as _  # type: ignore

from nextcloudappstore.core.models import App, AppRating

RATING_CHOICES = (
    (0.0, _('Bad')),
    (0.5, _('Ok')),
    (1.0, _('Good'))
)


class AppReleaseUploadForm(Form):
    download = CharField(label=_('Download link (tar.gz)'), max_length=256,
                         widget=TextInput(attrs={'required': 'required'}))
    signature = CharField(widget=Textarea(attrs={'required': 'required'}),
                          label=_('SHA512 signature'),
                          help_text=_(
                              'Can be generated by executing the '
                              'following command: openssl dgst -sha512 -sign '
                              '~/.nextcloud/certificates/APP_ID.key '
                              '/path/to/app.tar.gz | openssl base64'))
    nightly = BooleanField(label=_('Nightly'))


class AppRegisterForm(Form):
    certificate = CharField(
        widget=Textarea(attrs={'required': 'required'}),
        label=_('Public certificate'),
        help_text=_(
            'Usually stored in ~/.nextcloud/certificates/APP_ID.crt where '
            'APP_ID is your app\'s id. If you do not have a certificate you '
            'need to create a certificate sign request first which should be '
            'posted on the App Store\'s GitHub issue tracker. We will then '
            'post  you the signed certificate as answer. You can generate '
            'the sign request by  executing the following command: openssl '
            'req -nodes -newkey rsa:4096 -keyout APP_ID.key -out APP_ID.csr '
            '-subj "/CN=APP_ID"'))
    signature = CharField(widget=Textarea(attrs={'required': 'required'}),
                          label=_('SHA512 signature over your app\'s id'),
                          help_text=_(
                              'Can be generated by executing the following '
                              'command: echo -n "APP_ID" | openssl dgst '
                              '-sha512 -sign '
                              '~/.nextcloud/certificates/APP_ID.key | '
                              'openssl base64'))


class AppRatingForm(Form):
    def __init__(self, *args, **kwargs):
        self._id = kwargs.pop('id', None)
        self._user = kwargs.pop('user', None)
        self._language_code = kwargs.pop('language_code', None)
        super().__init__(*args, **kwargs)

    rating = ChoiceField(initial=0.5, choices=RATING_CHOICES,
                         widget=RadioSelect)
    comment = CharField(widget=Textarea, required=False,
                        label=_('Review'))

    class Meta:
        fields = ('rating', 'comment')

    def save(self):
        app = App.objects.get(id=self._id)
        app_rating, created = AppRating.objects.get_or_create(user=self._user,
                                                              app=app)
        app_rating.rating = self.cleaned_data['rating']
        app_rating.set_current_language(self._language_code)
        app_rating.comment = self.cleaned_data['comment']
        app_rating.save()
