# htcondor_status

Monitor [HTCondor][] clusters in your browser.

[HTCondor]: https://research.cs.wisc.edu/htcondor/


## Usage

Run as a server:

```
python -m htcondor_status serve --port 8500 --debug
```

Print all jobs as JSON to `stdout`:

```
python -m htcondor_status json --indent 2
```

or to a file:

```
python -m htcondor_status json --indent 2 --file out.json
```

Write static files to a directory:

```
python -m htcondor_status static /path/to/directory
```

## License

[MIT](LICENSE)

## Credits

The [Condor image][] was sourced from Wikipedia by user Colegota and licensed
[CC BY-SA 2.5 ES](https://creativecommons.org/licenses/by-sa/2.5/es/deed.en).

[Condor image]: https://en.wikipedia.org/wiki/File:Colca-condor-c03.jpg
