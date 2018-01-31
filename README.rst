================
Django SEO tools
================

.. image:: https://travis-ci.org/whyflyru/django-seo.svg?branch=master
    :target: https://travis-ci.org/whyflyru/django-seo?branch=master

.. image:: https://coveralls.io/repos/whyflyru/django-seo/badge.svg?branch=master
    :target: https://coveralls.io/r/whyflyru/django-seo?branch=master

This is a set of SEO tools for Django.
It allows you to associate metadata with:

* absolute paths
* model instances
* model classes
* views

Metadata can be edited in the admin in a centralised place, but also alongside any associated models.

This is however a framework, not an app. You therefore have
complete control over the data you store.
Here is an example of a definition:

.. code:: python

    from djangoseo import seo

    class BasicMetadata(seo.Metadata):
        title          = seo.Tag(max_length=68, head=True)
        keywords       = seo.KeywordTag()
        description    = seo.MetaTag(max_length=155)
        heading        = seo.Tag(name="h1")
        subheading     = seo.Tag(name="h2")
        extra          = seo.Raw(head=True)

        # Adding some fields for facebook (opengraph)
        og_title       = seo.MetaTag(name="og:title", populate_from="title", verbose_name="facebook title")
        og_description = seo.MetaTag(name="og:description", populate_from="description", verbose_name='facebook description')

As you can see it is very flexible, but there is much more than this simple example.

Installation
============

The easiest way to install Django SEO is to use use ``pip``, if you have it::

    pip install django-seo

If you don't, and you prefer the old school ``easy_install``, then the following command is for you::

    easy_install django-seo

Add ``djangoseo`` to your INSTALLED_APPS:

.. code:: python

    INSTALLED_APPS = (
        ...
        'djangoseo',
    )
    
Specify the path to migrations:

.. code:: python

    MIGRATION_MODULES = {
        'djangoseo': 'path.to.migrations',
    }

Optionally enable ``SEO_USE_REDIRECTS`` and specify ``SEO_TRACKED_MODELS`` if you need a functional of redirects:

.. code:: python

    SEO_USE_REDIRECTS = True  # for tracking 404 errors

    # for tracking models URLs
    SEO_TRACKED_MODELS = (
        'your_app.models.Foo',
        'your_app.models.Bar'
    )

Make migrations for ``django-seo`` models::
    
    $ manage.py makemigrations

And migrate your database::

    $ manage.py migrate

Usage
=====

Adding SEO to your Django site is easy, you need to do two things:

- Define which metadata fields you need
- Add the output to your templates
- Setup optional redirects

Metadata definition
--------------------

You can define which fields appear in your metadata by creating a class that subclasses ``seo.Metadata``. For example, create a new file called ``seo.py`` in an app on your site:

.. code-block:: python

    from djangoseo import seo

    class MyMetadata(seo.Metadata):
        title       = seo.Tag(head=True, max_length=68)
        description = seo.MetaTag(max_length=155)
        keywords    = seo.KeywordTag()
        heading     = seo.Tag(name="h1")

Done! The above definition outlines four fields:

- A ``<title>`` field, appearing in the head and limited to 68 characters (most search engines will the first 68 characters before any truncating takes place).
- A ``<meta>`` tag for the description, with a maximum length of 155 (again, to appear in search engine results). ``<meta>`` tags are always set to appear in the head.
- A ``<meta>`` tag for keywords. (you could also use ``seo.MetaTag``).
- A ``<h1>`` tag for headings, which does not appear in the document head.

If you run migrate you will also notice that four new models are created:

- One to attach the metadata to paths
- One to attach the metadata to model instances
- One to attach the metadata to models
- One to attach the metadata to views

Setting up the Admin
--------------------

To view and edit these in Django's admin, add the following to your ``urls.py``:

.. code-block:: python

    from djangoseo.admin import register_seo_admin
    from django.contrib import admin
    from myapp.seo import MyMetadata

    register_seo_admin(admin.site, MyMetadata)

You should now see the four models in the admin, and will be able to add metadata for each of the fields you defined earlier.

Adding the output to your templates
-----------------------------------

Once again, there isn't much to do here. Simply pick a suitable template. Most often this will be ``base.html``, which is extended by most other templates.
After loading the ``seo`` template library, simply output all the head elements add the tag ``{% get_metadata %}``, like this:

.. code-block:: html

    {% load seo %}
    <html>
    <head>
      {% get_metadata %}
    </head>
    <body>
        <p>I like gypsy Jazz!</p>
    </body>
    </html>

.. note::

   Make sure you have ``"django.core.context_processors.request"`` listed in your site's ``TEMPLATE_CONTEXT_PROCESSORS`` setting.
   This provides ``{% get_metadata %}`` with the current path, allowing it to automatically select the relevant metadata.

Seeing it in action
-------------------
Using the admin site, add some new metadata, attaching it to a (valid) path of your choice.
Open up your browser and visit the path, to hopefully see something like this in the page source:

.. code-block:: html

    <html>
    <head>
      <title>My Title</html>
      <meta name="description" content="My description" />
      <meta name="keywords" content="My, list, of, keywords" />
    </head>
    <body>
        <p>I like gypsy Jazz!</p>
    </body>
    </html>

Fine tuning the display
-----------------------

Notice that all of the head elements have automatically been added where the ``{% get_metadata %}`` tag was used.
But you'll also notice that the heading is missing.
Because the heading was not defined to appear in the head, it was not automatically added.
To do that, you will have to explicitly add it to the template. Like this:

.. code-block:: html

    {% load seo %}
    <html>
    <head>
      {% get_metadata as my_meta %}
      {{ my_meta }}
    </head>
    <body>
        {{ my_meta.heading }}
        <p>I like gypsy Jazz!</p>
    </body>
    </html>

Now your page will show the heading you wanted.
Notice that ``{% get_metadata %}`` no longer outputs the head metadata, but instead creates a new variable ``my_meta``. The line following it (``{{ my meta }}``) outputs the head elements for you, and can be used to access other fields, such as the heading.

But what if your ``<h1>`` needs to have a class?
You can also retrive the value directly, like this:

.. code-block:: html

        <h1 class="special">{{ my_meta.heading.value }}</h1>

Subdomains
----------

``django-seo`` supports subdomains, for example, via `django-subdomains <https://pypi.python.org/pypi/django-subdomains>`_ . In order to use subdomains support in your seo-model, specify the option ``use_subdomains``:

.. code-block:: python

    from djangoseo import seo

    class MyMetadata(seo.Metadata):
        title       = seo.Tag(head=True, max_length=68)
        description = seo.MetaTag(max_length=155)
        keywords    = seo.KeywordTag()
        heading     = seo.Tag(name="h1")

        class Meta:
            verbose_name = 'Meta tag'
            verbose_name_plural = 'Meta tags'
            use_subdomains = True

After that, you can specify a specific subdomain on which to display the metadata and redefine the subdomain in the template tag to output the data:

.. code-block:: html

    {% get_metadata SeoModelWithSubdomains under "msk" %}

Redirects
---------

Currently supported are two types of redirects: when an occurs error 404 and when model changes its URL on the site.
For each type of redirects used functional of `django.contrib.redirects <https://docs.djangoproject.com/en/1.10/ref/contrib/redirects/>`_. You must configure it before use redirects from ``django-seo``.

If you need a redirection when an error occurs 404, enable ``SEO_USE_REDIRECTS`` and setup URL patterns for redirection in admin interface.
It's like a standard URL patterns, but instead of finding a suitable view it creates a redirect in case of an error 404 for a given pattern.
For example for pattern ``/news/([\w\-_]+)/`` will be created a redirect for ``/news/foo/`` and ``/news/bar/``.

If you need a redirection when model changes its URL list the full path to the models in ``SEO_TRACKED_MODELS``:

.. code:: python

    SEO_TRACKED_MODELS = (
        'your_app.models.Foo',
        'your_app.models.Bar'
    )

Attention: each path to model must be direct and model must have a method ``get_absolute_url``.
Work such redirection follows: when path to model on site changed, it create redirection to old path.
For example:

.. code:: python

    class Foo(models.model):
        ...
        slug = models.SlugField(max_length=50)

        def get_absolute_url(self):
            return reverse('name-of-foo-url', kwargs={'slug': self.slug})

If you create instance of ``Foo``, redirection will not be created, but if change ``slug`` on instance of ``Foo`` ``django-seo`` creates new redirect for old instance path.
