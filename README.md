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
    ***
    <comments>
    ***
    <defn> = <body>;
    <defn> = <body>;
    ....
    <main> = <body>;
```
Where the body is composed of lambda terms. 

```
<body> = fn <lambdaname> => <body> |
         <name> <body>             |
         (<body>) <body>                 
```
where `name` is the name of a definition defined above. By defining terms like this, we can manipulate those terms and return terms based on those definitions. For example
```
    zero    = fn f => fn x => x
    one     = fn f => fn x => f (x)
    two     = fn f => fn x => f (f(x))
    three   = fn f => fn x => f (f(f(x)))
```
We can define integers like this.
How terms are reduced are defined by the rules of normal order reduction. 
To see more on normal order reduction, see this [link](https://opendsa-server.cs.vt.edu/OpenDSA/Books/PL/html/ReductionStrategies.html).
To see more on lambda calculus in general, see [here](https://en.wikipedia.org/wiki/Lambda_calculus).

## Example Use

Here is an example running of a test program `less.lc`. 


```
% sh lambdacalc.sh exampleprograms/less.lc 
fn succ_2750785 => fn succ_2750787 => succ_2750785 
%
%
```
Where the `main` of the file looks like
```
    main    = less one three;
```
And the return is equivalent to `true`, as defined in the file.
This and other example programs are discussed below.

## Other Example Programs

To see some example LambdaCalc++ programs, see `./exampleprograms`. There are examples of simple arithmatic, logic, and simple recursive programs.

## Possible Extensions

Here are some possible extensions to this project that were outside the scope or there was not enough time for.
- Efficency: As of now the code is horribly ineffecient. This is to be expected because the point of the project was to gain a better understanding of programming language basics. 
- Running Technique: The shell script and passing output files works but is hacky. Ideally if this were a real language the process from parsing to reducing woule be a more stable.
- Final answers: The final answers have intermediary names as of now (succ_203023). A function could be writted to replace these with cleaner names (f, n, s, etc.) so that the final answer is a bit cleaner.