from jinja2.environment import Environment

from dataride.configs import Infra


class Application:
    def __init__(self, jinja_environment: Environment, infra: Infra):
        self.jinja_environment = jinja_environment
        self.infra = infra

    def create_infra_setup(self, fmt: bool = True) -> None:
        """
        Creates the infrastructure setup based on the provided config file

        :param config_path: where YAML data platform config setup file is stored
        :param destination: where infrastructure code should be saved
        :param fmt: whether to execute `terraform fmt` on a destination directory after infrastructure generation
        :param verbose: whether to print more outputs
        """

        self.infra.process_modules()
        self.infra.process_resources()
        self.infra.process_environments()
        self.infra.process_extra_assets()

        self.infra.save()

        if fmt:
            self.infra.format_code()
