import glob
import os
import shutil

from flask.ext.assets import Bundle

def noop(_in, out, **kw):
    out.write(_in.read())

def register(assets, bundles):
    bundles["demo_js"] = Bundle(
#            "js/lib/jquery.js",
#            "js/lib/bootstrap.js",
#            "js/lib/jquery-ui.js",
            "../themes/demo/static/js/demo.js",
            filters='jsmin',
            output="assets/js/demo.js"
        )

    bundles["demo_css"] = Bundle(
#            "css/lib/bootstrap.css",
#            "css/lib/jquery-ui.css",
#            "css/lib/styles.css",
            "../themes/demo/static/css/demo.css",
            filters='cssmin',
            output="assets/css/demo.css"
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

    for font in glob.glob("piko/themes/demo/static/fonts/*.*"):
        shutil.copy(font, fonts_path)
        #assets.add(Bundle(font, filters=(noop,), output="fonts/%s" % (os.path.basename(font))))

    for image in glob.glob("piko/themes/demo/static/images/*.*"):
        shutil.copy(image, images_path)
        #assets.add(Bundle(image, filters=(noop,), output="images/%s" % (os.path.basename(image))))

    return bundles

