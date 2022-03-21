from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):

    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'Об авторе'
        context['author_text'] = 'Иван Варюхин'
        return context


class AboutTechView(TemplateView):

    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'Технологии'
        context['tech_text'] = ('Python 3.7<br>'
                                'Django 2.2.19')
        return context
