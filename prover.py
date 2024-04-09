from z3 import *

class State:
    def __init__(self, name):
        self.table = Function(f'{name}_table', IntSort(), BoolSort())
        self.hand = Function(f'{name}_hand', IntSort(), BoolSort())
        self.stacked = Function(f'{name}_stacked', IntSort(), IntSort(), BoolSort())
        self.clear = Function(f'{name}_clear', IntSort(), BoolSort())
        self.handsfree = Function(f'{name}_handsfree', IntSort(), BoolSort())

# here we need to extract z3 specs from current state, then add to our constraints
# if x is not clear but pickup states it is clear, we will have a contradiction
# clear blocks
# table blocks
# arm blocks


############## pick up constraints##############
the_block = 0
s1 = State('s1')
s2 = State('s2')
constraint1 = And(s1.table(the_block), s1.clear(the_block))
constraint2 = Not(s1.hand(the_block))
constraint3 = s2.hand(the_block)
constraint4 = And(Not(s2.table(the_block)), Not(s2.clear(the_block)))
x = Int('x')
fun = Function('fun', IntSort(), BoolSort())
constraint5 = ForAll([x], Implies(x != the_block, And(s1.table(x) == s2.table(x), s1.hand(x) == s2.hand(x), s1.clear(x) == s2.clear(x))))
x = Int('x')
y = Int('y')
constraint6 = ForAll([x, y], s1.stacked(x, y) == s2.stacked(x, y))
constraints = And(constraint1, constraint2, constraint3, constraint4, constraint5, constraint6)

solver = Solver()
solver.add(constraints)
out = solver.check() 
if out == sat:
    model = solver.model()
    print(model)
else:
    print("No soluZon found")
    # print(solver.unsat_core())