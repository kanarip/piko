from flask.ext.assets import Bundle

def register(assets, bundles):
    bundles["default_js"] = Bundle(
            "js/lib/jquery.js",
            "js/lib/bootstrap.js",
            "js/lib/jquery-ui.js",
            "js/piko.js",
            filters='jsmin',
            output="assets/js/piko.js"
        )

    bundles["default_css"] = Bundle(
            "css/lib/bootstrap.css",
            "css/lib/jquery-ui.css",
            "css/lib/styles.css",
            "css/piko.css",
            filters='cssmin',
            output="assets/css/piko.css"
        )

    return bundles
