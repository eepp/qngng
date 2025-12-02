# qngng

[![Latest version](https://img.shields.io/pypi/v/qngng.svg?label=Latest%20version)](https://pypi.python.org/pypi/qngng)

**_qngng_** is the _[Queb](https://en.wikipedia.org/wiki/Quebec) name generator: next generation_.

This is a fork (and then essentially a rewrite) of the more basic
[qng](https://github.com/abusque/qng) project which includes more
options.

Unfortunately, the qng maintainer is unresponsive and won't follow up
with community contributions, so this fork is necessary.

## Quick try

```
$ pipx run qngng
Annick Pinsonneault
```

## Features

* Generate a random Queb name from lists of popular Queb first names
  and surnames, from an existing [UDA](https://uda.ca/) directory
  member name, and/or from other lists:

  ```
  $ qngng
  Théodore Banville
  ```

  ```
  $ qngng --cat=uda-singers
  Daniel Boucher
  ```

  ```
  $ qngng --cat=lbl
  Stéphane-Albert Boulais
  ```

  ```
  $ qngng --cat=icip
  René Homier-Roy
  ```

  You can mix categories:

  ```
  $ qngng --cat=uda-singers --cat=std
  Karl-Hugo Van De Kerckhove
  ```

  The available categories are:

  | Category | Description |
  |----------|-------------|
  | `all` | All the categories. |
  | `d31` | [District 31](https://www.imdb.com/title/tt5954206/) characters. |
  | `dug` | [Dans une galaxie près de chez vous](https://www.imdb.com/title/tt0278857/) characters. |
  | `icip` | [ICI Première](https://ici.radio-canada.ca/premiere) personalities. |
  | `lbl` | [La bête lumineuse](https://www.onf.ca/film/bete_lumineuse/) characters. |
  | `sn` | [Série noire](https://www.imdb.com/title/tt3480144/) characters. |
  | `std` | Popular first names and surnames. |
  | `uda-actors` | UDA actor member names. |
  | `uda-hosts` | UDA host member names. |
  | `uda-singers` | UDA singer member names. |
  | `uda` | [UDA](https://uda.ca/) member names. |

* Generate a random male or female name:

  ```
  $ qngng --female
  Karen Cusson
  ```

  ```
  $ qngng --male --cat=uda-hosts
  Claude Poirier
  ```

* For the `std` (default) category, generate a double-barreled surname,
  a middle name, or a middle initial:

  ```
  $ qngng --double-surname
  Josiane Fiset-Bellerose
  ```

  ```
  $ qngng --middle-name --female
  Geneviève Margot Chartier
  ```

  ```
  $ qngng --middle-initial
  Coralie D. Trépanier
  ```

* Print the generated name with various formats:

  ```
  $ qngng --snake-case
  laura_viau
  ```

  ```
  $ qngng --kebab-case --cat=uda
  michel-mpambara
  ```

  ```
  $ qngng --camel-case --female --double-surname
  clemenceBriseboisGroulx
  ```

  ```
  $ qngng --cap-camel-case --male --cat=sn
  MarcArcand
  ```

See `qngng --help` for the complete list of options.

## Install qngng

To install qngng:

* Use [pipx](https://pipx.pypa.io/stable/installation/):

  ```
  $ pipx install qngng
  ```

## Name sources

The data sources of qngng are:

| Category | Source |
|----------|--------|
| `d31` | IMDB's [District 31](https://www.imdb.com/title/tt5954206/). |
| `dug` | FANDOM's [Dans une galaxie près de chez vous](https://dansunegalaxie.fandom.com/fr/wiki/Accueil) wiki. |
| `icip` | [List of ICI Première shows](https://ici.radio-canada.ca/premiere/emissions). |
| `lbl` | IMDB's [La bête lumineuse](https://www.imdb.com/title/tt0129807/). |
| `sn` | [Série noire](https://quijouequi.com/oeuvre/459/serie-noire) on _Qui Joue Qui?_. |
| `std` | L'[Institut de la statistique](http://www.stat.gouv.qc.ca/statistiques/population-demographie/caracteristiques/noms_famille_1000.htm) for surnames and [PrénomsQuébec.ca](https://www.prenomsquebec.ca/) for first names (who in turn get their data from Retraite Québec's [Banque de prénoms](https://www.rrq.gouv.qc.ca/fr/enfants/banque_prenoms/Pages/banque_prenoms.aspx)). |
| `uda*` | April 2019 UDA directory. |
