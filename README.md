# martha

Sits atop ninja to make building a bit more pleasant

## Check with mypy

~~~sh
MYPYPATH=$PWD mypy --check-untyped-defs --namespace-packages --follow-imports silent *.py cppbuild/*.py test/*.py
~~~

&hellip;or to watch for changes and run `mypy` on every update:

~~~sh
ls -1 *.py cppbuild/*.py test/*.py | entr -cs 'MYPYPATH=$PWD mypy --check-untyped-defs --namespace-packages --follow-imports silent *.py cppbuild/*.py test/*.py'
~~~
