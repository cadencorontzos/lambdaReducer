python3 parser.py $1
sml reducer.sml < prettyPrint.sml > out.txt
if [ "$2"  = "-v" ];
then
    grep "val it = ()"  out.txt | sed 's/val it = () : unit/ /g' | sed 's/-  / /g' | sed 's/|/\n/g'
else 
    grep "val it = ()"  out.txt | sed 's/val it = () : unit/ /g' | sed 's/-  / /g' | sed 's|.*\|||' 
fi
# rm prettyPrint.sml
# rm out.txt
