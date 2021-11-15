val _ = (Control.Print.printDepth := 100)

val freshVariableIndex = ref 0

(* Gives the base of a variable, findBase ex_1010 = ex, findBase f = f *)
fun findBase base nil       = base
  | findBase base (x::xs)   =   if (x=(#"_")) 
                                then base
                                else findBase (base^(str x)) xs

(* Adds a string to the end of a variable to avoid repeats *)
fun getFreshVariable v = 
    let val _ = (freshVariableIndex := (!freshVariableIndex) + 1)
        val i = (!freshVariableIndex)
        val base = (findBase (str (hd (explode v))) (tl (explode v)))
        in (base ^"_"^ (Int.toString i))
    end


(* LM = (fn n => <defn> ) , VA = variable, AP = application of any two of AP, LM, or VA *)
datatype lmda = 
        LM of string*lmda
    |   AP of lmda*lmda
    |   VA of string

(* Checks if a term is reducible by the rules of normal order reduction *)
fun isReducible (VA x)                = false
  | isReducible (AP(LM(x,t), s))      = true
  | isReducible (LM(x,t))             = isReducible t
  | isReducible (AP(t1,t2))           = (isReducible t1) orelse (isReducible t2)

fun replace x s (LM(f,p))  =  if f=x 
                              then (LM(f,p))
                              else  let
                                        val fresh = getFreshVariable x
                                    in
                                        (LM(fresh,(replace x s (replace f (VA fresh) p))))
                                    end

  | replace x s (AP(fs,sn)) = (AP((replace x s fs),(replace x s sn)))
  | replace x s (VA l)      =   if l=x 
                                then s 
                                else (VA l)

(* Carries out a single step of a normal order reduction *)
fun norReduceStep (AP(LM(x,t), s))  = (replace x s t)
  | norReduceStep (AP(t1,t2))       =   if (isReducible t1) 
                                        then (AP((norReduceStep t1),t2)) 
                                        else    if (isReducible t2) 
                                              then (AP(t1,(norReduceStep t2)))
                                              else (AP(t1,t2))
  | norReduceStep (LM(x,t))         = (LM(x,(norReduceStep t)))
  | norReduceStep (VA v)            = (VA v)

(* Convert lmda to string *)
fun pretty (VA v)       = v 
  | pretty (LM(s,t))    = "fn "^s^" => "^(pretty t)
  | pretty (AP(t1,t2))  = " "^(pretty t1)^"  ( "^(pretty t2)^" ) "

(* Reduces a lambda term *)
(* Take the print statement out if you're running recursive code. The output file will be several gigabytes. This needs to be fixed/worked around in some way *)
fun norReduce lm = if isReducible lm
                   then let 
                            val f = print (pretty lm)
                            val endl = print "|"
                        in 
                            norReduce (norReduceStep lm)
                        end
                    else
                        lm