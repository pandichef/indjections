"""
References:
https://www.valentinog.com/blog/drf/
https://blog.usejournal.com/serving-react-and-django-together-2089645046e4
"""
import os
import subprocess

settings = """
TEMPLATES[0]['DIRS'] += [os.path.join(BASE_DIR, 'reactapp')]
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'reactapp', "build", "static"),
)
import subprocess
from django.utils.autoreload import autoreload_started
from django.dispatch import receiver
@receiver(autoreload_started)
def rebuild_react_app(sender, **kwargs):
    sender.watch_dir(os.path.join(BASE_DIR, 'reactapp', 'src'), '*')
    if os.name == 'nt':
        subprocess.run(r'yarn --cwd .\\reactapp build', shell=True)
    else:
        subprocess.run(r'yarn --cwd ./reactapp build', shell=True)
"""

urls = """
from django.contrib.auth.decorators import login_required

@login_required
def react_view(request):
    return render(request, 'build/index.html')

urlpatterns += [path('react/', react_view, name='react_view')]
"""

def npx_create_react_app():
    if not os.path.exists('./reactapp'):
        subprocess.run("npx create-react-app reactapp", shell=True)
    else:
        print("Reactapp directory already exists.  Using existing installation...")

post_hooks = [
    npx_create_react_app,
]

def delete_react_app_folder():
    print('Attempting to delete ./reactapp...')
    subprocess.run("rm -ri ./reactapp", shell=True)

post_hooks_delete = [
    delete_react_app_folder,
]
