import math
import sympy as sp

InfoText = """
Just a little outside script to see how to solve the math problems in Stage 4
The tests from here are in the solver already, just needed a script to see how to solve these and deduct them.
"""

Tests = ['(36^2 + 81^2)^2 - 4*18*68',
         'math.floor((972 + 62) * 0.8)',
         'math.ceil((225 + 149)^2 / 98)',
         'math.round((261 * 138 + 721) / 704)',
         'a = 67, b = a + 74, c = b^2 - 278, x = c * (a + 1 - b)',
         'a = 27, b = a + 43 * a, x = b^2 - 80',
         'x/30 + 26 = 25^2',
         '(1! - 3!)^2 - 6!',
         '(22 + 86)(64 - 10) + 66^2'
         'Bottom Blue Hint: 1399196',
         'math.ceil(pi * 616 + 23)',
         '1 + 1',
         'Bottom Red Hint: 2162450',
         'Asap',
         '77 + 33',
         'a = 2425, b = 4703, return not not not not not not not (a == b)']


def formula_translation(n):
    if n.count('^') > 0:
        n = n.replace('^', '**')
    if n.count('pi') > 0:
        n = n.replace('pi', 'math.pi')
    if n.count('!') > 0:
        factorial_lib = {'1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5080, '8': 40640}
        for i in range(1, 9):
            if str(i) in n:
                n = n.replace(str(i) + '!', str(factorial_lib[str(i)]))
    if n.count(')(') > 0:
        n = n.replace(')(', ')*(')
    if n.count('math.round') > 0:
        n = n.replace('math.round', 'round')
    return n


def type2_equation_solver(equation_string):
    equations = equation_string.split(',')
    symbols = {}
    for eq in equations:
        eq = eq.strip()
        var, expr = eq.split('=')
        var = var.strip()
        expr = expr.strip()
        if var not in symbols:
            symbols[var] = sp.symbols(var)
        parsed_expr = sp.sympify(expr, locals=symbols)
        symbols[var] = parsed_expr
    return round({var: expr.evalf() for var, expr in symbols.items()}['x'])


def type1_equation_solver(equation):
    left, right = equation.split('=')
    x = sp.symbols('x')
    left_expr = sp.sympify(left.strip())
    right_expr = sp.sympify(right.strip())
    eq = sp.Eq(left_expr, right_expr)
    solution = sp.solve(eq, x)
    return solution[0]


def stage4_solving(form):
    form = formula_translation(form)
    special_formulas = {'Asap': 1, '1 + 1': 11, '77 + 33': 100}
    if form in special_formulas.keys():
        return special_formulas[form]
    elif form.count('Blue') > 0:
        res = int(form.split()[-1]) + 1
        return res
    elif form.count('Red') > 0:
        res = int(form.split()[-1]) - 1
        return res
    elif form.count('not') > 0:
        return 0
    if form.count('x') == 1 and form.count('a') > 0:
        return type2_equation_solver(form)
    elif form.count('x') > 0 and form.count('a') == 0:
        return type1_equation_solver(form)
    else:
        return eval(form) if eval(form) is not list else eval(form)[0]

print(stage4_solving('math.floor(3.14 * 720 + 915)'))
# for i in Tests:
#    print(stage4_solving(i))
