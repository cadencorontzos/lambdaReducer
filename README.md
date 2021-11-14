# lambdaReducer
A Lambda Reducing set of programs. The project consists of a language, LambdaCalc++, and a set of rules for that language, one that imitates lambda calculus. The language can be parsed in python by `parser.py` and then interpreted and reduced in sml by `reducer.sml`.

## Usage

This language can be ran by passing in a file, which is done as follows.
```
    sh lambdacalc.sh <input file> [options]
```
where `<input file>` is a `.lc` file. As of now there is only one optional flag
```
    Options:
        -v: verbose mode. Will show each reduction step as the main definition is parsed and reduced.
```

## LabmdaCalc++ Syntax

All LabmdaCalc++ files are files of plaintext with extension `.lc`. The file is a collection of defintions, along with a `main` definition in which the computation is carried out.
```
    <defn> = <body>
    <defn> = <body>
    ....
    <main> = <body>
```
Where the body is composed of lambda terms. 

```
<body> = fn <lambdaname> => <body> |
         <name> <body>             |
         (<body>) <body>                 
```
where `name` is the name of a definition defined above. 

## Example Use


## Other Example Programs

