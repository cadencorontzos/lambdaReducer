python3 parser.py $1
sml reducer.sml < prettyPrint.sml > out.txt
grep "val it = ()"  out.txt | sed 's/val it = () : unit/ /g' | sed 's/-  / /g' | sed 's/|/\n/g'
# rm out.txt
