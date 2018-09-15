# -*- coding: utf-8 -*-
import os
import sys
import webbrowser

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')

@task
def test(ctx):
    syntax(ctx)
    import pytest
    errcode = pytest.main(['tests'])
    sys.exit(errcode)

@task
def syntax(ctx):
    """Run pre-commit hooks on codebase. Checks formatting and syntax."""
    ctx.run('pre-commit run --all-files --show-diff-on-failure', echo=True)

@task
def watch(ctx):
    """Run tests when a file changes. Requires pytest-xdist."""
    import pytest
    errcode = pytest.main(['-f'])
    sys.exit(errcode)

@task
def clean(ctx):
    run('rm -rf build')
    run('rm -rf dist')
    run('rm -rf marshmallow-jsonapi.egg-info')
    clean_docs(ctx)
    print('Cleaned up.')

@task
def clean_docs(ctx):
    run('rm -rf %s' % build_dir, echo=True)

@task
def browse_docs(ctx):
    path = os.path.join(build_dir, 'index.html')
    webbrowser.open_new_tab(path)

def build_docs(ctx, browse):
    ctx.run('sphinx-build %s %s' % (docs_dir, build_dir), echo=True)
    if browse:
        browse_docs(ctx)

@task
def docs(ctx, clean=False, browse=False, watch=False):
    """Build the docs."""
    if clean:
        clean_docs(ctx)
    if watch:
        watch_docs(ctx, browse=browse)
    else:
        build_docs(ctx, browse=browse)

@task
def watch_docs(ctx, browse=False):
    """Run build the docs when a file changes."""
    try:
        import sphinx_autobuild  # noqa
    except ImportError:
        print('ERROR: watch task requires the sphinx_autobuild package.')
        print('Install it with:')
        print('    pip install sphinx-autobuild')
        sys.exit(1)
    ctx.run(
        'sphinx-autobuild {0} {1} {2} -z marshmallow_jsonapi'.format(
            '--open-browser' if browse else '', docs_dir, build_dir,
        ), echo=True, pty=True,
    )

@task
def readme(ctx, browse=False):
    run('rst2html.py README.rst > README.html', echo=True)
    if browse:
        webbrowser.open_new_tab('README.html')
