from traitlets import Unicode, Integer
from traitlets.config import Application
import tornado.ioloop
import tornado.web
from .github import GitHubBuildHandler

class BuilderApp(Application):
    config_file = Unicode(
        'builder_config.py',
        help="""
        Config file to load.

        If a relative path is provided, it is taken relative to current directory
        """,
        config=True
    )

    port = Integer(
        8585,
        help="""
        Port for the builder to listen on.
        """,
        config=True
    )

    docker_push_secret = Unicode(
        'docker-push-secret',
        help="""
        A kubernetes secret object that provides credentials for pushing built images.
        """,
        config=True
    )

    docker_image_prefix = Unicode(
        "",
        help="""
        Prefix for all built docker images.

        If you are pushing to gcr.io, you would have this be:
            gcr.io/<your-project-name>/

        Set according to whatever registry you are pushing to.

        Defaults to "", which is probably not what you want :)
        """,
        config=True
    )

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.load_config_file(self.config_file)
        self.tornado_settings = {
            "docker_push_secret": self.docker_push_secret,
            "docker_image_prefix": self.docker_image_prefix
        }

        self.tornado_app = tornado.web.Application([
            (r"/build/github/(\w+)/([a-zA-Z0-9_-]+)/(\w+)", GitHubBuildHandler),
        ], **self.tornado_settings)

    @classmethod
    def launch_instance(cls, argv=None):
        instance = cls.instance()
        instance.initialize()
        instance.tornado_app.listen(instance.port)
        tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    BuilderApp.launch_instance()