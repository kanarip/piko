import glob
import os
import shutil

from flask.ext.assets import Bundle

def noop(_in, out, **kw):
    out.write(_in.read())

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

    fonts_path = os.path.abspath(
            os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    '..',
                    'piko',
                    'static',
                    'assets',
                    'fonts'
                )
        )

    images_path = os.path.abspath(
            os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    '..',
                    'piko',
                    'static',
                    'assets',
                    'images'
                )
        )

    if not os.path.isdir(fonts_path):
        os.makedirs(fonts_path)

    if not os.path.isdir(images_path):
        os.makedirs(images_path)

    for font in glob.glob("piko/themes/default/static/fonts/*.*"):
        shutil.copy(font, fonts_path)
        #assets.add(Bundle(font, filters=(noop,), output="fonts/%s" % (os.path.basename(font))))

    for image in glob.glob("piko/themes/default/static/images/*.*"):
        shutil.copy(image, images_path)
        #assets.add(Bundle(image, filters=(noop,), output="images/%s" % (os.path.basename(image))))


    return bundles
