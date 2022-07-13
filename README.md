# htcondor_status

Monitor [HTCondor][] clusters in your browser.

[HTCondor]: https://research.cs.wisc.edu/htcondor/

## Installation

Create a conda environment:

```
conda env install -f environment.yml
conda activate htcondor-status
```

Install NPM dependencies:

```
(env) npm install
```

Generate the HTML, Javascript, and CSS:

```
(env) npm run build
```

## Usage

Run as a server:

```
python -m htcondor_status serve --port 8500 --debug
```

Write JSON files to be served by Apache, nginx, etc.:

```
python -m htcondor_status json /path/to/directory
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
