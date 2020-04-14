from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from core.forms import *
from core.mixins import CustomLoginRequiredMixin
from core.models import *


class AdDetailsView(DetailView):
    template_name = "ads/add_details.html"
    model = Ad
    slug_field = "id"
    slug_url_kwarg = "ad_id"
    context_object_name = "ad"

    def get_queryset(self):
        return self.model.objects.select_related("category").select_related("user").all()


class AdCreateView(CustomLoginRequiredMixin, CreateView):
    template_name = 'ads/create.html'
    form_class = AdCreateForm
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super(AdCreateView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AdCreateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            # print(self.request.FILES.getlist('image'))
            self.form_valid(form)
            files = self.request.FILES.getlist('image')
            for image in files:
                photo = AdImage(ad=self.object, image=image)
                photo.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)