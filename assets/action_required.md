# Welcome

Thank you for using the `dataride` toolkit for your infrastructure setup! 

If you have any questions or ideas, please feel free to reach out to us via [Github repository issues](https://github.com/mckraqs/dataride/issues).

# Action required

Even though we try to spare you as much mundane work as possible, you are still required to take some (minor) action. Unfortunately, it's not possible to read your mind and fill variables values upfront or decide where to store the state of the Terraform infrastructure.

Below you can find generated list of steps you need to take to fully make use of the provided setup. 

* **Backend** - please check your Terraform backend configurations and fill missing values for each environment separately: 
    {%- for env_name, env_config in envs.items() %}
    * env: {{ env_name }} (backend in: `<destination>/{{ env_name }}/main.tf`)
    {%- endfor %}
* **Module variables without default values** - plase check whether all module variables with no default value provided are managed in <u>each</u> environment
    {%- for module_name, module_config in modules.items() %}
    * module: {{ module_name }}
    {%- if module_config['vars_no_def']|length > 0 -%}
    {%- for var in module_config['vars_no_def'] %}
        * var: {{ var }}
    {%- endfor -%}
    {% else -%}
    {{ ' ' }}- no variables to check
    {% endif -%}
    {%- endfor %}
* **Environment variables without default values** - please check environment variables to fill missing values if no default was provided in a config file.
    {%- for env_name, env_config in envs.items() %}
    * env: {{ env_name }}
    {%- if env_config['variables']|length > 0 -%}
    {%- for var in env_config['variables'] %}
        * var: {{ var }}
    {%- endfor -%}
    {% else -%}
    {{ ' ' }}- no variables to check
    {% endif -%}
    {% endfor %}
* **Initialize the environments** - before running `terraform plan/apply`, for each environment execute `terraform init` to fetch all the necessary TF files

Happy further development!
