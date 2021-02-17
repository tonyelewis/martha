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

## CI Errors

An apparently spurious `flake8` error under Python 3.7 but not 3.8 like this:

~~~no-highlight
text/text_region.py:1:7: E999 SyntaxError: invalid syntax
import bisect
      ^
1     E999 SyntaxError: invalid syntax
1
~~~

&hellip;is likely due to `flake8` failing to deal with a 3.8-style debug f-string somewhere else in the source, eg:

~~~python
f'{value=}'
~~~
