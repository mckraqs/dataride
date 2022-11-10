from dataride.configs import Infra
from dataride.utils import prepare_jinja_environment, load_config


class Application:
    def __init__(self):
        self.jinja_environment = prepare_jinja_environment()

    def create_infra_setup(self, config_path: str, destination: str, fmt: bool = True, verbose: bool = False) -> None:
        """
        Creates the infrastructure setup based on the provided config file

        :param config_path: where YAML data platform config setup file is stored
        :param destination: where infrastructure code should be saved
        :param fmt: whether to execute `terraform fmt` on a destination directory after infrastructure generation
        :param verbose: whether to print more outputs
        """
        config_infra = load_config(config_path)
        infra = Infra(config_infra, destination, self.jinja_environment, verbose)

        infra.process_modules()
        infra.process_resources()
        infra.process_environments()
        infra.process_extra_assets()

        infra.save()
        infra.format_code(fmt)
