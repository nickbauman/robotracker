from routes import application as default_application

MODULE_APPLICATIONS = {
    # example:
    #'migration': routes_migration,
}


def build_uri(route_name, params_dict={}, module=None):
    application = MODULE_APPLICATIONS.get(module, default_application)
    return application.router.build(None, route_name, None, params_dict)
