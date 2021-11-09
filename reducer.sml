val _ = (Control.Print.printDepth := 100)

val freshVariableIndex = ref 0

(* fun getFreshVariable v = 
    let val _ = (freshVariableIndex := (!freshVariableIndex) + 1)
        val i = (!freshVariableIndex)
        val base = ... strip out _ with explode and implode...
        in (base ^ (Int.toString i))
    end *)

datatype lmda = 
        LM of string*lmda
    |   AP of lmda*lmda
    |   VA of string


fun replace x s (LM(f,p))  =  if f=x 
                              then (LM(s,(replace x s p)))
                              else (LM(f,(replace x s p)))
  | replace x s (AP(fs,t)) = (AP((replace x s fs),(replace x s t)))
  | replace x s (VA l)     =  if l=x 
                              then (s) 
                              else (VA l)

fun norReduce (VA s)            = (VA s)
  | norReduce (AP((LM(x,t)),s)) = (replace x s t)
  | norReduce (LM(x,t))         = (LM(x,(norReduce t)))
  | norReduce (AP(AP(t1,t2),t3))= if (norReduce t1) <> t1 
                                  then (AP(AP((norReduce t1),t2),t3))
                                  else  if (norReduce t2) <> t2
                                        then   AP(AP(t1,(norReduce t2)),t3)
                                        else AP(AP(t1,t2),t3)
  | norReduce (AP(t1,t2))       = if (norReduce t1) = t1 
                                  then AP(t1,(norReduce t2))
                                  else AP(t1,t2)