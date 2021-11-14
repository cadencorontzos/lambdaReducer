#   The code is first parsed by the python parser. The parser will make the whole 
#   file into a single term to be reduced. It will then 'pretty print' that term into an sml
#   friendly file (a let in end statement). SMl then carries out the reduction of this file
#   then the steps are output into out.txt. Either all the steps or just the final product
#   (based off the precence of the verbose flag) are then grabbed and printed to the console.

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
